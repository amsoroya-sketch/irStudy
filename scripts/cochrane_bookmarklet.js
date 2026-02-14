// Cochrane Download Bookmarklet
// Drag this to your bookmarks bar in Firefox
// Click it while on a Cochrane Review page to download the HTML

javascript:(function(){
    var title = document.querySelector('h1').innerText;
    var doi = window.location.pathname.match(/CD\d+/)[0];

    // Create filename
    var filename = doi + '_' + title.replace(/[^a-z0-9]/gi, '_').substring(0,50) + '.html';

    // Get full page HTML
    var html = document.documentElement.outerHTML;

    // Create download
    var blob = new Blob([html], {type: 'text/html'});
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();

    alert('Downloaded: ' + filename);
})();
