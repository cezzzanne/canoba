$(function(){
	
	// Agrega las clases css a los métodos de pago
	$("#opciones-pago-wrap ul li").click(function(){
		$("#opciones-pago-wrap ul li").removeClass("checked-pago")
		$("input[name=tipo_pago]:checked").parent().parent().addClass("checked-pago")
	})

	// Envia el formulario con los datos de envio
	var datos_envio = []

	
	// Autollenado de campos del formulario de pago 

	$("#autofill-form").change(function(){
		if(this.checked) {
			$(".card-form .autof").each(function(i, el){
				$(el).prop("disabled", true)
				$(el).val(datos_envio[i])
			})
		}else{

			$(".card-form input:disabled").each(function(i, el){
				// Guardamos los datos iniciales en el arreglo datos_envio
				$(el).prop("disabled", false)
				$(el).val("")
			})
		}
	})

	// Muestra el formulario de los datos de envio para editarlos
	$("#editar-info-envio").click(function(e){
		e.preventDefault();
		$("#datos_envio_form").attr("action", "/guardar_datos_envio/" + "?e=1&pid="+$(this).data("pid"))
	    $("#confirm-info-wrap").slideUp("fast")
		$('#wrapper-form').slideDown("fast")

	})

	// Muestra las formas de pago
	$("#pagar_lnk").click(function(e){
		e.preventDefault();
		$("#editar-info-envio").hide()
		$(this).hide()
		$("#opciones-pago-wrap").slideDown("fast")
	})



	 // ======================================================
	 // 
	 // Conekta Public Key
	  Conekta.setPublishableKey('key_NLFkdKzLdpLLHP6zMB3ya8Q');
	 
	 // Tokenize the card
	  $("#card-form").submit(function(event) {
	  	alert("tu mama");
	  	console.log("tu mama");
	    var $form;
	    $form = $(this);
	    // console.log("tu mama");
	    // alert("tu mama");

	    
	/* Previene hacer submit más de una vez */

	    $form.find("button").prop("disabled", true);
	    Conekta.token.create($form, conektaSuccessResponseHandler, conektaErrorResponseHandler);

	    var conektaSuccessResponseHandler;
		conektaSuccessResponseHandler = function(token) {
			alert("sucess");
			var $form;
			$form = $("#card-form");
			
			/* Inserta el token_id en la forma para que se envíe al servidor */
			$form.append($("<input type=\"hidden\" name=\"conektaTokenId\" />").val(token.id));

			  
			/* and submit */
			$form.get(0).submit();
		};

		var conektaErrorResponseHandler;
		conektaErrorResponseHandler = function(response) {
			alert("not sucess");
			var $form;
		  	$form = $("#card-form");
		  
			/* Muestra los errores en la forma */
		  	$form.find(".card-errors").text(response.message);
		  	$form.find("button").prop("disabled", false);
		};

	    
	/* Previene que la información de la forma sea enviada al servidor */

	    return false;
	  });


})