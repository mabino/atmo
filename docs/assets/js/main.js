// Main JavaScript for Atmo website

$(document).ready(function() {
  // Smooth scrolling for anchor links
  $('a[href^="#"]').on('click', function(event) {
    var target = $(this.getAttribute('href'));
    if (target.length) {
      event.preventDefault();
      $('html, body').stop().animate({
        scrollTop: target.offset().top - 100
      }, 1000);
    }
  });

  // Add active class to navigation based on scroll position
  $(window).scroll(function() {
    var scrollDistance = $(window).scrollTop();

    $('section').each(function(i) {
      if ($(this).position().top <= scrollDistance + 200) {
        $('.main-nav a.active').removeClass('active');
        $('.main-nav a').eq(i).addClass('active');
      }
    });
  });

  // Add animation to feature cards on scroll
  $(window).scroll(function() {
    $('.feature-card').each(function() {
      var elementTop = $(this).offset().top;
      var elementBottom = elementTop + $(this).outerHeight();
      var viewportTop = $(window).scrollTop();
      var viewportBottom = viewportTop + $(window).height();

      if (elementBottom > viewportTop && elementTop < viewportBottom) {
        $(this).addClass('animate');
      }
    });
  });

  // Copy code blocks functionality
  $('.code-block').each(function() {
    var $codeBlock = $(this);
    var $copyButton = $('<button class="copy-button"><i class="fas fa-copy"></i></button>');

    $codeBlock.append($copyButton);

    $copyButton.on('click', function() {
      var text = $codeBlock.find('code').text();
      navigator.clipboard.writeText(text).then(function() {
        $copyButton.html('<i class="fas fa-check"></i>');
        setTimeout(function() {
          $copyButton.html('<i class="fas fa-copy"></i>');
        }, 2000);
      });
    });
  });
});