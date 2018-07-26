$(() => {
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
    const $searchButton = $('#main-nav .search.item')
    const $closeSearchButton = $('#site-search .close.item')
    
    /* bindings */
    $mobileNav
        .sidebar('attach events', $menuButton)
        .sidebar('setting', {
            exclusive: true,
            dimPage: false,
            scrollLock: true,
            onChange: () => {
                $('.sidebar.icon').toggle()
                $('#main-nav .times.icon').toggle()
            }
        })
    
    $siteSearch
        .sidebar('attach events', $searchButton, 'open')
        .sidebar('attach events', $closeSearchButton, 'close')
        .sidebar('setting', {
            exclusive: true,
            dimPage: false,
            closable: false,
            transition: 'push',
            onChange: () => {
                if ($('#main-nav .right.menu').css('visibility') == 'hidden') {
                    $('#main-nav .right.menu').css('visibility', 'visible')
                }
                else {
                    $('#main-nav .right.menu').css('visibility', 'hidden')
                }
            },
            onShow: () => setTimeout(() => $('#site-search #id_query')[0].focus(), 1),
            onHide: () => setTimeout(() => $('#site-search #id_query')[0].blur(), 1)
        })
    
    $('.ui.dropdown').dropdown()
    $('.ui.checkbox').checkbox()
});