// ── MEGA.nz Integration Service ──
// Loads comic PDFs from a public MEGA folder via client-side JS.
// Uses megajs loaded from esm.sh for the MEGA protocol (crypto + API).
//
// Usage:
//   const ms = await MegaService.init('https://mega.nz/folder/XXXX#YYYY');
//   const files = ms.getFiles();              // [{ name, path, size, ... }]
//   const stream = await ms.stream(file);     // ReadableStream for PDF.js
//   const url = await ms.getDownloadUrl(file); // Blob URL fallback

(function (root, factory) {
    if (typeof define === 'function' && define.amd) define([], factory);
    else if (typeof module === 'object' && module.exports) module.exports = factory();
    else root.MegaService = factory();
}(typeof self !== 'undefined' ? self : this, function () {

    var MEGA_CDN = 'https://esm.sh/megajs@1.2.0';
    var _folderUrl = '';
    var _files = [];
    var _mega = null;
    var _ready = false;
    var _initPromise = null;

    // ── Parse MEGA folder URL ──
    function parseFolderUrl(url) {
        // https://mega.nz/folder/XXXX#YYYY
        // https://mega.nz/folder/XXXX#YYYY!ZZZ  (with additional key)
        var m = url.match(/\/folder\/([A-Za-z0-9_-]+)#([A-Za-z0-9_,_-]+)/);
        if (!m) throw new Error('Invalid MEGA folder URL. Expected: https://mega.nz/folder/ID#KEY');
        return { folderId: m[1], key: m[2] };
    }

    // ── Dynamically import megajs ──
    async function loadMegaLib() {
        if (_mega) return _mega;
        try {
            // Dynamic import from esm.sh
            var mod = await import(MEGA_CDN);
            _mega = mod.default || mod;
            return _mega;
        } catch (e) {
            // Fallback: try jsdelivr
            try {
                var mod2 = await import('https://cdn.jsdelivr.net/npm/megajs@1.2.0/+esm');
                _mega = mod2.default || mod2;
                return _mega;
            } catch (e2) {
                // Last fallback: script tag injection
                return new Promise(function (resolve, reject) {
                    var script = document.createElement('script');
                    script.src = 'https://cdn.jsdelivr.net/npm/megajs@1.2.0/dist/main.min.js';
                    script.onload = function () { _mega = window.Mega || window.megajs; resolve(_mega); };
                    script.onerror = reject;
                    document.head.appendChild(script);
                });
            }
        }
    }

    // ── List public folder ──
    async function listFolder(folderUrl) {
        var mega = await loadMegaLib();
        var parsed = parseFolderUrl(folderUrl);

        // Try public folder API
        var storage;
        if (mega.Mega && mega.Mega.publicFolder) {
            storage = await mega.Mega.publicFolder(folderUrl);
        } else if (mega.publicFolder) {
            storage = await mega.publicFolder(folderUrl);
        } else if (mega.Storage && mega.Storage.publicFolder) {
            storage = await mega.Storage.publicFolder({ url: folderUrl });
        } else {
            // Manual fetch via MEGA REST API
            return await listFolderManual(parsed);
        }

        return flattenChildren(storage.children || [], '');
    }

    // ── Flatten MEGA folder tree ──
    function flattenChildren(children, prefix) {
        var result = [];
        (children || []).forEach(function (child) {
            var name = child.name || 'unknown';
            var fullPath = prefix ? prefix + '/' + name : name;
            if (child.directory) {
                var sub = flattenChildren(child.children, fullPath);
                result = result.concat(sub);
            } else {
                result.push({
                    name: name,
                    path: fullPath,
                    size: child.size || 0,
                    directory: false,
                    nodeId: child.nodeId || child.id || child.hash,
                    key: child.key,
                    _megaNode: child
                });
            }
        });
        return result;
    }

    // ── Manual MEGA REST API (no megajs needed) ──
    async function listFolderManual(parsed) {
        var folderId = parsed.folderId;
        var keyStr = parsed.key;

        // Decode the key (MEGA base64 variant)
        var keyBytes = base64ToBytes(keyStr.replace(/,/g, ''));

        // Call MEGA API to list folder
        var reqId = Math.floor(Math.random() * 1000000);
        var url = 'https://g.api.mega.co.nz/cs?id=' + reqId + '&n=' + folderId;
        var resp = await fetch(url, {
            method: 'POST',
            body: JSON.stringify([{ a: 'f', c: 1, ca: 1, r: 1 }])
        });
        var data = await resp.json();
        if (!data || !data[0]) throw new Error('MEGA API returned empty response');
        var nodes = data[0].f || [];
        var files = [];
        nodes.forEach(function (node) {
            if (node.t !== 0 && node.t !== 1) return; // 0=file, 1=folder
            var name = node.a && node.a.n ? atob(node.a.n) : 'unknown';
            files.push({
                name: name,
                path: name,
                size: node.s || 0,
                directory: node.t === 1,
                nodeId: node.h,
                key: keyBytes,
                _raw: node
            });
        });
        return files.filter(function (f) { return !f.directory; });
    }

    // ── MEGA base64 variant ──
    function base64ToBytes(b64) {
        // MEGA uses a variant of base64: replace - with + and _ with /
        b64 = b64.replace(/-/g, '+').replace(/_/g, '/');
        // Pad
        while (b64.length % 4) b64 += '=';
        var binary = atob(b64);
        var bytes = new Uint8Array(binary.length);
        for (var i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
        return bytes;
    }

    // ── Stream a file ──
    async function streamFile(fileObj) {
        if (_mega && fileObj._megaNode) {
            // Use megajs download
            return fileObj._megaNode.download();
        }
        // Manual download via MEGA REST API
        var reqId = Math.floor(Math.random() * 1000000);
        var url = 'https://g.api.mega.co.nz/cs?id=' + reqId;
        var resp = await fetch(url, {
            method: 'POST',
            body: JSON.stringify([{ a: 'g', g: 1, p: fileObj.nodeId }])
        });
        var data = await resp.json();
        if (!data || !data[0]) throw new Error('Failed to get download URL');
        var dl = data[0];
        var dlUrl = 'https://' + dl.g[0] + '.userstorage.mega.co.nz/' + dl.g[1] + '?id=' + dl.g[2];
        var fileResp = await fetch(dlUrl);
        return fileResp.body;
    }

    // ── Get a Blob URL for PDF.js ──
    async function getBlobUrl(fileObj) {
        var stream = await streamFile(fileObj);
        if (stream instanceof ReadableStream) {
            var reader = stream.getReader();
            var chunks = [];
            while (true) {
                var result = await reader.read();
                if (result.done) break;
                chunks.push(result.value);
            }
            var blob = new Blob(chunks, { type: 'application/pdf' });
            return URL.createObjectURL(blob);
        }
        // If it's a Readable (Node.js style), convert
        if (typeof stream.on === 'function') {
            return new Promise(function (resolve, reject) {
                var chunks = [];
                stream.on('data', function (chunk) { chunks.push(chunk); });
                stream.on('end', function () {
                    var blob = new Blob(chunks, { type: 'application/pdf' });
                    resolve(URL.createObjectURL(blob));
                });
                stream.on('error', reject);
            });
        }
        throw new Error('Unknown stream type');
    }

    // ── Public API ──
    return {
        // Initialize with a MEGA folder URL
        // Returns { files: [...], megaUrl: '...' }
        init: async function (folderUrl) {
            if (_initPromise) return _initPromise;
            _initPromise = (async function () {
                _folderUrl = folderUrl;
                try {
                    _files = await listFolder(folderUrl);
                    // Filter only PDFs
                    _files = _files.filter(function (f) {
                        return f.name && f.name.toLowerCase().endsWith('.pdf');
                    });
                    _ready = true;
                    console.log('[MegaService] Loaded ' + _files.length + ' PDFs from MEGA');
                } catch (e) {
                    console.error('[MegaService] Init failed:', e);
                    _ready = false;
                    throw e;
                }
                return { files: _files, megaUrl: folderUrl };
            })();
            return _initPromise;
        },

        getFiles: function () { return _files; },

        isReady: function () { return _ready; },

        stream: streamFile,

        getBlobUrl: getBlobUrl,

        // For PDF.js: returns either a Blob URL or the raw stream
        getPdfSource: async function (fileObj) {
            try {
                var blobUrl = await getBlobUrl(fileObj);
                return blobUrl;
            } catch (e) {
                console.warn('[MegaService] getPdfSource failed:', e);
                throw e;
            }
        }
    };
}));