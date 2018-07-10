import PitBar from './snippets/pitbar'

$(document).ready(function(){
    var $ribbon = $('.ribbon');
    if ($ribbon) {
        var faded = sessionStorage.getItem('fade-test-banner', true);
        if (! faded) {
            $('.ribbon-box').removeClass('fade');
        }
        $ribbon.on('click',function(){
            $('.ribbon-box').addClass('fade');
            sessionStorage.setItem('fade-test-banner', true);
        });
    }

    /* dom */
    const $mainNav = $('#main-nav')
    const $mobileNav = $('#mobile-nav')
    const $siteSearch = $('#site-search')
    const $menuButton = $('.toc.item')
    const $searchButton = $('.search.item')

    /* bindings */
    new PitBar($mainNav, $mobileNav)

    $mobileNav
        .sidebar('attach events', $menuButton)
        .sidebar('setting', {
            onChange: () => {
                // swap the hamburger icon for a close icon
                $('.times.icon').toggle()
                $('.sidebar.icon').toggle()
            }
    })

    $siteSearch
        .sidebar('attach events', $searchButton)
});