// Settings for accounting.js
accounting.settings = {
	currency: {
		symbol : "$ ",   // default currency symbol is '$'
		format: "%s%v MXN.", // controls output: %s = symbol, %v = value/number (can be object: see below)
		decimal : ".",  // decimal point separator
		thousand: ",",  // thousands separator
		precision : 2   // decimal places
	},
	number: {
		precision : 0,  // default precision on numbers is 0
		thousand: ",",
		decimal : "."
	}
}

$(function(){
	$(".money-fmt").each(function(k,v){ 
		$(v).text(accounting.formatMoney($(v).text()))
	});
  $("#carousel-example-generic").addClass("container");


  $("#close-wishlist").click(function(e){
  	e.preventDefault();
  	$("#wishlist-wrapper").slideUp("fast");
  });

  $("#wishlist-link, #wishlist-link-mob ").click(function(e){
  	e.preventDefault();
  	$("#wishlist-wrapper").slideToggle("fast");

  });
});

function isNumber(evt) {
    evt = (evt) ? evt : window.event;
    var charCode = (evt.which) ? evt.which : evt.keyCode;
    if (charCode > 31 && (charCode < 48 || charCode > 57)) {
        return false;
    }
    return true;
}

function goBack() {
	window.history.back()
}

// imprime el contenido de un elemento
function printData(element_id)
{
   var divToPrint=document.getElementById(element_id);
   newWin= window.open("");
   newWin.document.write(divToPrint.outerHTML);
   newWin.print();
   newWin.close();
}
