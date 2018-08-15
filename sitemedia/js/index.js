import 'babel-polyfill'
import { fromEvent } from 'rxjs'
import 'rxjs/add/operator/pluck'
import 'rxjs/add/operator/distinctUntilChanged'
import 'rxjs/add/operator/debounceTime'

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
    const $mobileNav = $('#mobile-nav')
    const $siteSearch = $('#site-search')
    const $menuButton = $('.toc.item')
    const $searchButton = $('#main-nav .search.item')
    const $closeSearchButton = $('#site-search .close.item')
    const $query = $('#id_query')

    /* observables */
    window.queryStream = fromEvent($query, 'input')
        .pluck('target', 'value')
        .debounceTime(500)
        .distinctUntilChanged()
    
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
});