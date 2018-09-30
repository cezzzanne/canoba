$(function(){
	// damos formato al precio default
	$("#precio").text(accounting.formatMoney($("#precio").text()))
	$(".money-fmt").each(function(k,v){ 
		$(v).text(accounting.formatMoney($(v).text()))
	});

	$("#material").on("change", function(){
		$(".preload-gif").fadeIn("fast")
		/*
		if($(this).find(':selected').data("name") == "Lienzo Liso"){
			$("#material-img").attr("src", "/static/img/mat_liso" + ".jpg")
		}
		*/
		if($(this).find(':selected').data("name") == "Texturizado"){
			$("#material-img").attr("src", "/static/img/mat_text" + ".jpg")
			$("#nomb-mat").text("Texturizado");
		}
		if($(this).find(':selected').data("name") == "Canvas"){
			$("#material-img").attr("src", "/static/img/mat_canvas" + ".jpg")
			$("#nomb-mat").text("Canvas");
		}
		if($(this).find(':selected').data("name") == "Vinipiel"){
			$("#material-img").attr("src", "/static/img/mat_vinipiel" + ".jpg")
			$("#nomb-mat").text("Vinipiel");
		}

		d = { "pk":$(this).val() }
		$.ajax({
			url:"/ajax/material/",
			data:d,
			type:"get",
			success:function(data){
				// cambio de precio depende del material y le damos formato moneda
				price = accounting.formatMoney(data[0].fields.precio1)
				$("#precio").text(price)

				// trigger del evento change en el select material
				$("#medidas").change()
			}
		})
			$(".preload-gif").fadeOut("fast")
	})

	$("#medidas").on("change", function(){
		$("#preload-gif").fadeIn("fast")
		d = { "pk":$("#material").val() }
		val = $(this).val()
		$("#diseno-img").attr("src", $(this).find(':selected').data('img'))
		$.ajax({
			url:"/ajax/material/",
			data:d,
			type:"get",
			success:function(data){
				price = accounting.formatMoney(data[0].fields["precio"+val])
				$("#precio").text(price)
			}
		})
		$("#preload-gif").fadeOut("fast")
	})

	$("#orientacion").on("change", function(){
		d = { "or" : $(this).val(), 
			  "pk" :$("#dis-pk").val() };
		t = this;
		$.ajax({
			url: "/ajax/orientacion/",
			data: d,
			type: "get",
		}).done(function(data){
			out = "";
			if(data.length > 0) {
				if (data[0].status == "error") {

					$(".modal-body").text(data[0].message)
					$(".modal-footer .btn").hide();
					button = '<button type="button" class="btn btn-primary aceptar-error" data-dismiss="modal">Aceptar</button>';
					$(".modal-footer").append(button);
					$("#myModal").modal();
					out += "<option>No tiene medidas disponibles</option>";
					$("#add-cart-btn").slideUp("fast");
					$("#medidas").html(out);

				} 
				else
				{
					for( i=0; i < data.length; i++ ) {
						out += "<option data-img='"+data[i].imagen+"' value='"+data[i].medida+"'>"+data[i].disp+"</option>";
					}
					$("#medidas").html(out);
					$("#medidas").change();
				}	
			}
			else 
			{
				if($(t).val() == "horizontal"){
					$("#orientacion").val("horizontal");	
				}
				else{
					$("#orientacion").val("vertical");	
				}

				$(".modal-body").text("Este diseño no cuenta con tamaños en orientación " + $("#orientacion").val())
				$(".modal-footer .btn").hide();
				button = '<button type="button" class="btn btn-primary aceptar-error" data-dismiss="modal">Aceptar</button>';
				$(".modal-footer").append(button);
				$("#myModal").modal();
				console.log($("#orientacion").val());
				//$("#orientacion").change();

			}
		})
	});

	$("#add-cart-btn").click(function(e){
		e.preventDefault()
		$(".modal-footer .btn").show();
		$(".aceptar-error").hide();
		$(".modal-body").text("Su producto se agregó correctamente al carrito, ¿Que desea hacer?");
		href = $(this).attr("href")
		precio = $("#precio").text().split(" MXN.")[0].split("$ ")[1]
		href += "&sz=" + $("#medidas").val() + "&mt=" + $("#material").val() + "&hor=" + $("#orientacion").val()
		$("#btn-seguir").attr("href", href + "&car=0")
		$("#btn-carrito").attr("href", href + "&car=1")
		//window.location.href = href
	})

	$("#btn-wish").click(function(e){
		e.preventDefault()
		href = $(this).attr("href")
		precio = $("#precio").text().split(" MXN.")[0].split("$ ")[1]
		href += "&sz=" + $("#medidas").val() + "&mt=" + $("#material").val() + "&hor=" + $("#orientacion").val() + "&wish=1"
		window.location.href = href
	})
	// Carrito Scritps

	$(".qty").change(function(){
		input_id = "#" + $(this).attr("id")
		update_qty($(input_id).val(), input_id.split("-")[1])
	})

	$(".dec-qty").click(function(e){
		e.preventDefault()
		input_id = "#" + $(this).data("in")
		if(Number($(input_id).val()) > 1){
			$(input_id).val(Number($(input_id).val()) - 1)
		}
		update_qty($(input_id).val(), input_id.split("-")[1])
	})

	$(".inc-qty").click(function(e){
		e.preventDefault()
		input_id = "#" + $(this).data("in")
		$(input_id).val(Number($(input_id).val()) + 1)
		update_qty($(input_id).val(), input_id.split("-")[1])
	})
})

function update_qty(qty, id){
	url = '/set_qty/?qty='+qty+'&pk='+id
	window.location.href = url
}