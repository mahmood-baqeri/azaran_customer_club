$(document).ready(function($) {
    "use strict";

    //  File input styling

    if ($("input[type=file].with-preview").length) {
        $("input.file-upload-input").MultiFile({
            list: ".file-upload-previews"
        });
    }

    $(".single-file-input input[type=file]").change(function() {
        previewImage(this);
    });

    $(".has-child a[href='#'].nav-link").on("click", function(e) {
        e.preventDefault();
        if (
            !$(this)
                .parent()
                .hasClass("hover")
        ) {
            $(this)
                .parent()
                .addClass("hover");
        } else {
            $(this)
                .parent()
                .removeClass("hover");
        }
    });

    if ($(".owl-carousel").length) {
        var galleryCarousel = $(".gallery-carousel");

        galleryCarousel.owlCarousel({
            loop: false,
            margin: 0,
            nav: true,
            items: 1,
            navText: [
                "<i class='fa fa-chevron-left'></i>",
                "<i class='fa fa-chevron-right'></i>"
            ],
            autoHeight: true,
            dots: false
        });

        $(".tabs-slider").owlCarousel({
            loop: false,
            margin: 0,
            nav: false,
            items: 1,
            autoHeight: true,
            dots: false,
            mouseDrag: true,
            touchDrag: false,
            pullDrag: false,
            freeDrag: false
        });

        $(".full-width-carousel").owlCarousel({
            loop: true,
            margin: 10,
            nav: true,
            items: 3,
            navText: [
                "<i class='fa fa-chevron-left'></i>",
                "<i class='fa fa-chevron-right'></i>"
            ],
            autoHeight: false,
            center: true,
            dots: false,
            autoWidth: true,
            responsive: {
                768: {
                    items: 3
                },
                0: {
                    items: 1,
                    center: false,
                    margin: 0,
                    autoWidth: false
                }
            }
        });

        $(".gallery-carousel-thumbs").owlCarousel({
            loop: false,
            margin: 20,
            nav: false,
            dots: true,
            items: 5,
            URLhashListener: true
        });

        $("a.owl-thumb").on("click", function() {
            $("a.owl-thumb").removeClass("active-thumb");
            $(this).addClass("active-thumb");
        });

        galleryCarousel.on("translated.owl.carousel", function() {
            var hash = $(this)
                .find(".active")
                .find("img")
                .attr("data-hash");
            $(".gallery-carousel-thumbs")
                .find("a[href='#" + hash + "']")
                .trigger("click");
        });
    }

    //  Form Validation

    $(".form.email .btn[type='submit']").on("click", function(e) {
        var button = $(this);
        var form = $(this).closest("form");
        button.prepend("<div class='status'></div>");
        form.validate({
            submitHandler: function() {
                $.post("assets/php/email.php", form.serialize(), function(
                    response
                ) {
                    button.find(".status").append(response);
                    form.addClass("submitted");
                });
                return false;
            }
        });
    });
});
