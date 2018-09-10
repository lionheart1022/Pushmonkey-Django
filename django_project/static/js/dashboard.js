$(function() {

  var chromeDefaultTitle = $("#chrome-title").html();
  var chromeDefaultMessage = $("#chrome-message").html();
  var firefoxDefaultTitle = $("#firefox-title").html();  
  var firefoxDefaultMessage = $("#firefox-message").html();    
  var safariDefaultTitle = $("#firefox-title").html();
  var safariDefaultMessage = $("#firefox-message").html();  
  $('#dashboard form .form-control').unbind('keyup change input paste').bind('keyup change input paste',function(e){

    var $this = $(this);
    var val = $this.val();
    var valLength = val.length;
    var maxCount = $this.attr('maxlength');
    if(valLength>maxCount){

      $this.val($this.val().substring(0, maxCount));
    }
  }); 
  $('#title').on('input', function() {

    var el = $(this);
    var val = el.val().substring(0, 20);
    if (val.length > 0) {

      $('#chrome-title').html(val);
      $('#firefox-title').html(val);
      $('#safari-title').html(val);
    } else {

      $('#chrome-title').html(chromeDefaultTitle);    
      $('#firefox-title').html(firefoxDefaultTitle);
      $('#safari-title').html(safariDefaultTitle);      
    }
  });
  $('#message').on('input', function() {

    var el = $(this);
    var val = el.val().substring(0, 80);
    if (val.length > 0) {

      $('#chrome-message').html(val);
      $('#firefox-message').html(val);
      $('#safari-message').html(val);      
    } else {

      $('#chrome-message').html(chromeDefaultMessage);      
      $('#firefox-message').html(firefoxDefaultMessage);
      $('#safari-message').html(firefoxDefaultMessage);      
    }
  });
  $("textarea.code").focus(function() {
      var $this = $(this);
      $this.select();

      // Work around Chrome's little problem
      $this.mouseup(function() {
          // Prevent further mouseup intervention
          $this.unbind("mouseup");
          return false;
      });
  });
  $("#custom-notification").submit(function(ev){

    ev.preventDefault();
    var values = $(this).serializeArray();
    var empty = false;
    var excluded_fields = ["scheduled_at"];
    $.each(values, function(i, v){

      var excluded = false;
      if (excluded_fields.indexOf(v["name"]) != -1) {

        excluded = true;
      }
      if (v["value"].trim().length === 0 && !excluded) {

        empty = true;
        return;
      }
    });
    if (empty) {

      alert("All fields are required.");
      return;
    }
    var url = "/push_message";
    var formData = new FormData($(this)[0]); 
    $.ajax({
      type: "POST",
      url: url,
      data: formData,
      cache: false,
      contentType: false,
      processData: false,      
      success: function(data, status) {

        if (status == "success") {

          $('#custom-notification-success').modal();
          $('#send-notification form input#title, #send-notification form input[name=url_args]').val('');
          $('#send-notification form textarea').val('');
        } else {

          $('#custom-notification-failed').modal();          
        }
      },
      error: function(req, status, error) {

        $('#custom-notification-failed').modal();          
      }
    });
  });
  if ($('#account_keys').length > 0) {

    $('#account_keys').multiselect({
            nonSelectedText: 'Please select at least one website'
        });    
  }
  if ($('#send_to_segments').length > 0) {

    $('#send_to_segments').multiselect({
            nonSelectedText: 'Please select at least one topic'
        });       
  }

  $('#datetimepicker').datetimepicker({
    sideBySide: true,
    showToday: true,
    format: "MM/DD/YYYY H:mm A",
    widgetPositioning: {
      horizontal: 'left'
   }
  });
  $("#scheduled_at").focus(function(){

    $('.input-group-addon').click();
  });
});