// $('#slider1, #slider2, #slider3').owlCarousel({
//     loop: true,
//     margin: 20,
//     responsiveClass: true,
//     responsive: {
//         0: {
//             items: 1,
//             nav: false,
//             autoplay: true,
//         },
//         600: {
//             items: 3,
//             nav: true,
//             autoplay: true,
//         },
//         1000: {
//             items: 5,
//             nav: true,
//             loop: true,
//             autoplay: true,
//         }
//     }
// })



$('.category-slider').owlCarousel({
    loop: true,
    margin: 20,
    responsiveClass: true,
    responsive: {
        0: { items: 1, nav: false, autoplay: true },
        600: { items: 3, nav: true, autoplay: true },
        1000: { items: 5, nav: true, loop: true, autoplay: true }
    }
});














// ---------------------- PLUS CART -----------------------
$('.plus-cart').click(function(){
    let id = $(this).attr("pid");

    $.ajax({
        type: "GET",
        url: "/pluscart",
        data: { prod_id: id },
        success: function(data){
            // Update product quantity in main cart
            $('.quantity[data-pid="' + id + '"]').text(data.quantity);

            // Update same product quantity in summary section
            $('.summary-quantity[data-pid="' + id + '"]').text('Qty: ' + data.quantity);

            // Update totals
            $('#amount').text('₹' + data.amount);
            $('#total-amount').text('₹' + data.total_amount);

            // Update cart badge
            if (data.cart_count !== undefined) {
                $('#cart-count').text(data.cart_count);
            }
        }
    });
});


// ---------------------- MINUS CART -----------------------
$('.minus-cart').click(function(){
    let id = $(this).attr("pid");

    $.ajax({
        type: "GET",
        url: "/minuscart",
        data: { prod_id: id },
        success: function(data){
            if (data.quantity > 0) {
                $('.quantity[data-pid="' + id + '"]').text(data.quantity);
                $('.summary-quantity[data-pid="' + id + '"]').text('Qty: ' + data.quantity);
            } else {
                // Remove from both main cart & summary
                $('.cart-item[data-id="' + id + '"]').remove();
                $('.summary-quantity[data-pid="' + id + '"]').closest('li').remove();
            }

            // Update totals
            $('#amount').text('₹' + data.amount);
            $('#total-amount').text('₹' + data.total_amount);

            // Update badge
            if (data.cart_count !== undefined) {
                $('#cart-count').text(data.cart_count);
            }

            // Empty cart message if everything deleted
            if (data.amount === 0) {
                $('.col-sm-8').html('<h4 class="text-center text-muted">Your cart is empty 😔</h4>');
                $('.col-sm-4 .card-body').html('<p class="text-muted small mb-0">Your cart is empty.</p>');
            }
        }
    });
});


// ---------------------- REMOVE CART -----------------------
$('.remove-cart').click(function(e){
    e.preventDefault();
    let id = $(this).attr('pid');

    $.ajax({
        type: "GET",
        url: "/removecart",
        data: { prod_id: id },
        success: function(data){
            // Remove product from both sections
            $('.cart-item[data-id="' + id + '"]').remove();
            $('.summary-quantity[data-pid="' + id + '"]').closest('li').remove();

            // Update totals
            $('#amount').text('₹' + data.amount);
            $('#total-amount').text('₹' + data.total_amount);

            // Update badge
            if (data.cart_count !== undefined) {
                $('#cart-count').text(data.cart_count);
            }

            // Empty cart message if no items
            if (data.amount === 0) {
                $('.col-sm-8').html('<h4 class="text-center text-muted">Your cart is empty 😔</h4>');
                $('.col-sm-4 .card-body').html('<p class="text-muted small mb-0">Your cart is empty.</p>');
            }
        }
    });
});


