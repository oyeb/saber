/*
	Spectral by HTML5 UP
	html5up.net | @n33co
	Free for personal and commercial use under the CCA 3.0 license (html5up.net/license)
*/

(function($) {

	skel
		.breakpoints({
			xlarge:	'(max-width: 1680px)',
			large:	'(max-width: 1280px)',
			medium:	'(max-width: 980px)',
			small:	'(max-width: 736px)',
			xsmall:	'(max-width: 480px)'
		});

	$(function($) {

		var	$window = $(window),
			$body = $('body'),
			$wrapper = $('#page-wrapper'),
			$banner = $('#banner'),
			$header = $('#header');

		// Disable animations/transitions until the page has loaded.
			$body.addClass('is-loading');

			$window.on('load', function() {
				window.setTimeout(function() {
					$body.removeClass('is-loading');
				}, 100);
			});

		// Mobile?
			if (skel.vars.mobile)
				$body.addClass('is-mobile');
			else
				skel
					.on('-medium !medium', function() {
						$body.removeClass('is-mobile');
					})
					.on('+medium', function() {
						$body.addClass('is-mobile');
					});

		// Fix: Placeholder polyfill.
			$('form').placeholder();

		// Prioritize "important" elements on medium.
			skel.on('+medium -medium', function() {
				$.prioritize(
					'.important\\28 medium\\29',
					skel.breakpoint('medium').active
				);
			});

		// Scrolly.
			$('.scrolly')
				.scrolly({
					speed: 1500,
					offset: $header.outerHeight()
				});

		// Menu.
			$('#menu')
				.append('<a href="#menu" class="close"></a>')
				.appendTo($body)
				.panel({
					delay: 500,
					hideOnClick: true,
					hideOnSwipe: true,
					resetScroll: true,
					resetForms: true,
					side: 'right',
					target: $body,
					visibleClass: 'is-menu-visible'
				});

		// Header.
			if (skel.vars.IEVersion < 9)
				$header.removeClass('alt');

			if ($banner.length > 0
			&&	$header.hasClass('alt')) {

				$window.on('resize', function() { $window.trigger('scroll'); });

				$banner.scrollex({
					bottom:		$header.outerHeight() + 1,
					terminate:	function() { $header.removeClass('alt'); },
					enter:		function() { $header.addClass('alt'); },
					leave:		function() { $header.removeClass('alt'); }
				});

			}

			 $.timeliner({
				startOpen:['#19550828', '#19630828'],
			});
			$.timeliner({
				timelineContainer: '#timeline-js',
				timelineSectionMarker: '.milestone',
				oneOpen: true,
				startState: 'flat',
				expandAllText: '+ Show All',
				collapseAllText: '- Hide All',
				startOpen: ['#born']
			});
			// Colorbox Modal
			$(".CBmodal").colorbox({inline:true, initialWidth:100, maxWidth:682, initialHeight:100, transition:"elastic",speed:750});


			var nt_example2 = $('#bob').newsTicker({
			row_height: 60,
			max_rows: 1,
			speed: 300,
			duration: 6000,
			prevButton: $('#bob-prev'),
			nextButton: $('#bob-next'),
			hasMoved: function() {
		    	$('#bob-infos-container').fadeOut(200, function(){
		        	$('#bob-infos .infos-hour').text($('#bob li:first span').text());
		        	$('#bob-infos .infos-text').text($('#bob li:first').data('infos'));
		        	$(this).fadeIn(400);
		        });
		    },
		    pause: function() {
		    	$('#bob li i').removeClass('fa-play').addClass('fa-pause');
		    },
		    unpause: function() {
		    	$('#bob li i').removeClass('fa-pause').addClass('fa-play');
		    }
		});
		$('#bob-infos').hover(function() {
		    nt_example2.newsTicker('pause');
		}, function() {
		    nt_example2.newsTicker('unpause');
		});

	});

})(jQuery);
