// ── MEGA.nz Integration Service ──
// Loads comic PDFs from a public MEGA folder via client-side JS.
// Uses megajs (loaded via script tag in index.html) for MEGA protocol.
//
// Usage:
//   var ms = await MegaService.init('https://mega.nz/folder/XXXX#YYYY');
//   ms.getFiles()  => [{ name, path, size, _megaNode }]

(function (root, factory) {
    if (typeof define === 'function' && define.amd) define([], factory);
    else if (typeof module === 'object' && module.exports) module.exports = factory();
    else root.MegaService = factory();
}(typeof self !== 'undefined' ? self : this, function () {

    var _files = [];
    var _ready = false;
    var _initPromise = null;

    // ── Get megajs instance ──
    function getMega() {
        var m = window.Mega || window.megajs;
        if (!m) throw new Error('megajs not loaded');
        return m;
    }

    // ── List public folder via megajs ──
    async function listFolder(folderUrl) {
        var Mega = getMega();
        var storage = await Mega.publicFolder(folderUrl);
        return flatten(storage.children || []);
    }

    // ── Flatten tree to flat file list ──
    function flatten(children) {
        var result = [];
        (children || []).forEach(function (child) {
            if (child.directory) {
                result = result.concat(flatten(child.children));
            } else {
                result.push({
                    name: child.name,
                    path: child.name,
                    size: child.size || 0,
                    _megaNode: child
                });
            }
        });
        return result;
    }

    // ── Stream a file via megajs → Blob URL ──
    async function getBlobUrl(fileObj) {
        var stream = fileObj._megaNode.download();
        var reader = stream.getReader();
        var chunks = [];
        while (true) {
            var r = await reader.read();
            if (r.done) break;
            chunks.push(r.value);
        }
        return URL.createObjectURL(new Blob(chunks, { type: 'application/pdf' }));
    }

    // ── Public API ──
    return {
        init: async function (folderUrl) {
            if (_initPromise) return _initPromise;
            _initPromise = (async function () {
                try {
                    _files = await listFolder(folderUrl);
                    _files = _files.filter(function (f) {
                        return f.name && f.name.toLowerCase().endsWith('.pdf');
                    });
                    _ready = true;
                    console.log('[MegaService] Loaded ' + _files.length + ' PDFs');
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
        getPdfSource: async function (fileObj) {
            return getBlobUrl(fileObj);
        }
    };
}));