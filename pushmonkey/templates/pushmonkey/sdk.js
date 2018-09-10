var PushMonkey = function(config) {

  var pm = this;
  pm.fireUp = function() {

    if (pm.isSafari) {

      pm.querySafariPermissions();
    } else if (pm.isSubFrame) {

      pm.queryPermissions();
    } else if (pm.isNotWordpress) {
      
      window.addEventListener("message", pm.receiveMessage, false);
      pm.createSubFrame();
    } else if (pm.isHttps || pm.isPopUp) {

      if (pm.hasServiceWorkers) {

        if (pm.isPopUp) {
        
          pm.registerServiceWorker();
        } else {

          if (pm.isDemo) {

            window.addEventListener("message", pm.receiveMessage, false);
            pm.createSubFrame();
          } else {
            
            pm.registerLocalServiceWorker();
          }
        }
      } else {

        pm.log("Push Monkey: Service workers are not available.");
      }        
    } else {

      window.addEventListener("message", pm.receiveMessage, false);
      pm.createSubFrame();
    }
  }
  pm.throwError = function(e) {

      throw Error(e);
  }
  pm.log = function(m) {

      1 == pm.debug && console.log(m);
  }
  pm.registerServiceWorker = function() {

    navigator.serviceWorker.register(pm.serviceWorker).then(pm.initialiseState);
  }
  pm.registerLocalServiceWorker = function() {

    navigator.serviceWorker.register(pm.serviceWorkerLocal).then(pm.initialiseState);
  }  
  pm.initialiseState = function(registration) {

    registration.update();
    // Are Notifications supported in the service worker?
    if (!pm.serviceWorkersSupportNotifications) {

      pm.log('Notifications aren\'t supported.');
      return;
    }
    // Check the current Notification permission. If its denied, it's a 
    // permanent block until the user changes the permission.
    if (Notification.permission === 'denied') {

      pm.log('The user has blocked notifications.');
      return;
    }
    pm.log("initialiseState. We can proceed.");
    // We need the service worker registration to check for a subscription
    navigator.serviceWorker.ready.then(function(serviceWorkerRegistration) {

      // Do we already have a push message subscription?
      pm.log("initialiseState. Service worker ready.")
      serviceWorkerRegistration.pushManager.getSubscription().then(function(subscription) {

          pm.log("initialiseState. Got subscription status.");
          if (!subscription) {

            pm.subscribe();
          } else {

            // Already subscribed.
            pm.log("initialiseState. Already subscribed.");
          }
        }).catch(function(err) {

          pm.log('Error during getSubscription()', err);
        });
    }).catch(function(err) {

      pm.log("Error activating service worker", err);
    });
  }    
  pm.receiveMessage = function(ev) {

    pm.log(ev);
    if (ev.origin != pm.sdkHost) return;
    if (ev.data == "allowed") {
    
      pm.showDialog();
    } else if (typeof ev.data == "object") {

      if (ev.data[0] == "subscribed") {

        pm.retrieveSegments(ev.data[1]);
      }
    }
  }
  pm.showDialog = function() {

    var link = document.createElement("a");
    link.setAttribute('href',"#");
    link.setAttribute('onclick',"window._pushmonkey.openWindow();");  
    link.setAttribute("style", "display: block; background-color: "+pm.dialogButtonBackgroundColor+"; width: 70px; border-radius: 5px; margin: 15px auto 0 auto; padding: 5px; color: black;");
    link.innerHTML = "Close";
    var header = document.createElement("h3");
    header.setAttribute("style", "line-height: 20px; margin: 0; font-size: 18px;");
    header.innerHTML = "Thank you for subscribing!";
    var dialog = document.createElement("div");
    dialog.setAttribute("id", "pm_dialog");
    var top = window.innerHeight/3 - 50;
    var left = window.innerWidth/2 - 100;
    dialog.setAttribute("style", "background-color: "+pm.dialogBackgroundColor+"; position: absolute; top: "+top+"px; left: "+left+"px; width: 200px; height: 110px; text-align: center; padding: 10px; border-radius: 10px;");
    dialog.appendChild(header);
    dialog.appendChild(link);
    var overlay = document.createElement("div");
    overlay.setAttribute("style", "background-color: rgba(0, 0, 0, 0.32); position: absolute; z-index: 9999; width: 100%; height: 100%; top: 0; left: 0;");
    overlay.appendChild(dialog);
    overlay.setAttribute("id", "pm_overlay");
    document.body.appendChild(overlay);     
  } 
  pm.hideDialog = function() {

    document.getElementById("pm_overlay").remove();
  }
  pm.openWindow = function() {

    pm.hideDialog();
    var top = window.innerHeight/2 - 50;
    var left = window.innerWidth/2 - 100;
    pm.popupWindow = window.open(pm.windowSrc, "Subscribing...", "scrollbars=yes, width=200, height=100, top="+top+", left="+left);
  }
  pm.createSubFrame = function() {

    var iframe = document.createElement("iframe");
    iframe.setAttribute("id", "pm_iframe");
    iframe.setAttribute("src", pm.windowSrc);
    iframe.style.width = "0px";
    iframe.style.height = "0px";
    iframe.style.border = "0px";
    iframe.setAttribute("visibility", "hidden");
    iframe.style.display = "none";
    document.body.appendChild(iframe);  
  } 
  pm.queryPermissions = function() {

    navigator.permissions.query({

        name: "notifications"
    }).then(function(p) {

      p.onchange = function() {

        pm.log("Permission changed");
        pm.log(p.state);
        if (p.state == "allowed" || p.state == "granted") {

          // tell the parent to open window
          window.parent.postMessage("allowed", "*");
        }
      }
      if (p.state == "default" || p.state == "prompt") {

        Notification.requestPermission();          
      }
    });      
  }   
  pm.querySafariPermissions = function() {

    pm.requestSafariPermissions();
  } 
  pm.requestSafariPermissions = function() {

    window.safari.pushNotification.requestPermission(
      pm.safariEndpointURL,
      pm.safariWebPushID, 
      {
        url: window.location.href
      },
      function(p) {

        pm.log(p);
        if (pm.getCookie("pm_topics") != "yes") {
          
          pm.retrieveSegments(p.deviceToken);
          pm.setCookie("pm_topics", "yes", 180);
        }
      })
  }  
  pm.subscribe = function() {

    navigator.serviceWorker.ready.then(function(registration) {

      registration.pushManager.subscribe({userVisibleOnly: true}).then(function(subscription) {

          pm.sendSubscriptionToServer(subscription);
        }).catch(function(e) {

          if (Notification.permission === 'denied') {

            // The user denied the notification permission which
            // means we failed to subscribe and the user will need
            // to manually change the notification permission to
            // subscribe to push messages
            pm.log('Permission for Notifications was denied');
          } else {

            // A problem occurred with the subscription, this can
            // often be down to an issue or lack of the gcm_sender_id
            // and / or gcm_user_visible_only
            pm.log('Unable to subscribe to push notificatins.');
            pm.log(e);              
          }
        });
    });
  }
  pm.endpointWorkaround = function(pushSubscription) {

    // Make sure we only mess with GCM
    if (pushSubscription.endpoint.indexOf('https://android.googleapis.com/gcm/send') !== 0) {

      return pushSubscription.endpoint;
    }

    var mergedEndpoint = pushSubscription.endpoint;
    // Chrome 42 + 43 will not have the subscriptionId attached
    // to the endpoint.
    if (pushSubscription.subscriptionId &&
      pushSubscription.endpoint.indexOf(pushSubscription.subscriptionId) === -1) {
      // Handle version 42 where you have separate subId and Endpoint
      mergedEndpoint = pushSubscription.endpoint + '/' +
        pushSubscription.subscriptionId;
    }
    return mergedEndpoint;
  }    
  pm.sendSubscriptionToServer = function(subscription) {

    // For compatibly of Chrome 43, get the endpoint via
    // endpointWorkaround(subscription)
    // e.g.
    pm.log(subscription);
    var mergedEndpoint = pm.endpointWorkaround(subscription);
    var url = pm.sdkHost + "/push/v1/register/" + pm.accountKey;
    jQuery.ajax({
          type: "POST",
          url: url,
          crossDomain: true,
          data: jQuery.param({"endpoint": mergedEndpoint}),
          success: function (data) {

            pm.didSendSubscriptionToServer(data, mergedEndpoint);
          },
          error: function (err) {

            pm.log("sendSubscriptionToServer error: ");
            pm.log(error);
            if (pm.isPopUp) {

              window.close();
            }
          }
    });
  }
  pm.didSendSubscriptionToServer = function(data, endpoint) {

    pm.log("sendSubscriptionToServer saved: ");
    pm.log(data); 
    pm.log(endpoint);
    if (pm.isPopUp) {

      window.opener.postMessage(["subscribed", endpoint], "*");
      window.close();
    } else {

      pm.retrieveSegments(endpoint);
    }
  }
  pm.retrieveSegments = function(endpoint) {

    if (!pm.segmentationEnabled) {

      pm.log("Segmentation is disabled.");
      return;
    }
    var url = pm.sdkHost + "/push/v1/segments/" + pm.accountKey + "?backgroundColor=" + encodeURIComponent(pm.dialogBackgroundColor);
    jQuery.ajax({
          type: "POST",
          url: url,
          crossDomain: true,
          data: jQuery.param({"endpoint": endpoint}),
          success: function (data) {

            if (data.segments) {
              
              if (data.segments.length > 0) {
                
                pm.showSegmentsDialog(data.template, endpoint);
              }
            } else {

              pm.log("error retrieving segments: ");
              pm.log(data);
            }
          },
          error: function (err) {

            pm.log("error retrieving segments: ");
            pm.log(err);
          }
    });
  }
  pm.showSegmentsDialog = function(template, token) {

    var dialog = document.createElement("div");
    dialog.setAttribute("id", "pm_segments_dialog");
    var dialogWidth = window.innerWidth/2;
    var top = window.innerHeight/3 - 50;
    var left = window.innerWidth/2 - dialogWidth/2;
    dialog.setAttribute("style", "background-color: "+pm.dialogBackgroundColor+"; top: "+top+"px; left: "+left+"px; width: "+dialogWidth+"px; text-align: left; padding: 10px; border-radius: 10px;");
    dialog.innerHTML = template;
    var overlay = document.createElement("div");
    overlay.setAttribute("style", "background-color: rgba(0, 0, 0, 0.32); position: absolute; z-index: 9999; width: 100%; height: 100%; top: 0; left: 0;");
    overlay.appendChild(dialog);
    overlay.setAttribute("id", "pm_overlay");
    document.body.appendChild(overlay); 
    var saveLink = document.getElementById("pm_segments_save");
    var cancelLink = document.getElementById("pm_segments_cancel");    
    saveLink.onclick = function(){

      var segments = []
      document
      .querySelectorAll('#pm_segments_dialog input:checked')
      .forEach(function(v, i){ 

        segments.push(v.value);
      });
      saveLink.innerHTML = "Saving...";
      saveLink.onclick = function(){};
      pm.saveSegments(segments, token, saveLink);
    }; 
    cancelLink.onclick = function() {

        pm.hideSegmentsDialog();
    }   
  }
  pm.saveSegments = function(segments, token, button) {

    var url = pm.sdkHost + "/push/v1/segments/save/" + pm.accountKey;
    jQuery.ajax({
          type: "POST",
          url: url,
          crossDomain: true,
          data: jQuery.param({"segments": segments, "token": token}),
          success: function (data) {

            console.log(data);
            button.innerHTML = "Awesome!"
            setTimeout(function(){

              pm.hideSegmentsDialog();              
            }, 2000);
          },
          error: function (err) {

            pm.log("error retrieving segments: ");
            pm.log(err);
          }
    });    
  }
  pm.hideSegmentsDialog = function() {

    document.getElementById("pm_overlay").remove()
  }
  pm.setCookie = function(cname, cvalue, exdays) {

    var d = new Date();
    d.setTime(d.getTime() + (exdays*24*60*60*1000));
    var expires = "expires="+ d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
  }
  pm.getCookie = function(cname) {
      var name = cname + "=";
      var decodedCookie = decodeURIComponent(document.cookie);
      var ca = decodedCookie.split(';');
      for(var i = 0; i <ca.length; i++) {
          var c = ca[i];
          while (c.charAt(0) == ' ') {
              c = c.substring(1);
          }
          if (c.indexOf(name) == 0) {
              return c.substring(name.length, c.length);
          }
      }
      return "";
  }
  pm.checkIfFirefox = function() {

      var browser = pm.checkBrowser().split("-");
      return "Firefox" == browser[0] && "44" <= browser[1] ? 1 : 0
  }
  pm.checkBrowser = function() {

    var a = navigator.userAgent,
        d = navigator.appName,
        e = "" + parseFloat(navigator.appVersion);
    parseInt(navigator.appVersion, 10);
    var c = "",
        g, f,
        k; 
    - 1 != (f = a.indexOf("OPR/")) ? (d = "Opera", e = a.substring(f + 4)) : -1 != (f = a.indexOf("Opera")) ? (d = "Opera", e = a.substring(f + 6), -1 != (f = a.indexOf("Version")) && (e = a.substring(f + 8))) : -1 != (f = a.indexOf("MSIE")) ? (d = "Microsoft Internet Explorer", e = a.substring(f + 5)) : -1 != (f = a.indexOf("Chrome")) ? (d = "Chrome", e = a.substring(f + 7), /(.*?)wv\)/.test(a) && (c = "22")) : -1 != (f = a.indexOf("Safari")) ? (d = "Safari", e = a.substring(f + 7), -1 != (f = a.indexOf("Version")) && (e = a.substring(f + 8))) : -1 != (f = a.indexOf("Firefox")) ? (d = "Firefox", e = a.substring(f +
        8)) : (g = a.lastIndexOf(" ") + 1) < (f = a.lastIndexOf("/")) && (d = a.substring(g, f), e = a.substring(f + 1), d.toLowerCase() == d.toUpperCase() && (d = navigator.appName)); - 1 != (k = e.indexOf(";")) && (e = e.substring(0, k)); - 1 != (k = e.indexOf(" ")) && (e = e.substring(0, k));
    a = parseInt("" + e, 10);
    isNaN(a) && (e = "" + parseFloat(navigator.appVersion), a = parseInt(navigator.appVersion, 10));
    "22" == c && (a = c);
    return d + "-" + a + "-" + e
  }  
  pm.checkIfChrome = function() {

    var b = pm.checkBrowser().split("-");
    return 1 != pm.deviceType && "48" <= b[1] ? 1 : "Chrome" == b[0] && "42" <= b[1] ? 1 : 0
  }
  pm.checkIfSafari = function() {

      var a = window.navigator.userAgent,
          d = a.indexOf("Safari"),
          e = a.indexOf("Chrome"),
          a = a.substring(0,
              d).substring(a.substring(0, d).lastIndexOf("/") + 1);
      return /iPad|iPhone|iPod/.test(navigator.userAgent) ? 0 : -1 == e && 0 < d && 7 <= parseInt(a, 10) ? 1 : 0
  }
  pm.getDevice = function() {

    navigator.userAgent.toLowerCase();
    return pm.isTablet() ? 2 : pm.isMobile() ? 3 : 1
  }  
  pm.isTablet = function(a) {

    if (/android/.test(a)) {

        if (!1 === /mobile/.test(a)) return 1
    } else if (!0 === /ipad/.test(a)) return 1;
    return 0
  }
  pm.isMobile = function() {

    return /(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino|android|ipad|playbook|silk/i.test(navigator.userAgent || navigator.vendor || window.opera) || /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test((navigator.userAgent ||
        navigator.vendor || window.opera).substr(0, 4));
  }
  pm.getOS = function() {

      var a = navigator.userAgent.toLowerCase();
      return /windows phone/i.test(a) ? 6 : /android/i.test(a) ? 4 : /ipad|iphone|ipod/.test(a) && !window.MSStream ? 5 : /linux/i.test(a) ? 2 : /macintosh|mac os x/i.test(a) ? 3 : /windows|win32/i.test(a) ? 1 : 7
  }
  pm.accountKey = config.accountKey;
  pm.debug = config.debug;
  pm.deviceType = pm.getDevice();
  pm.isDemo = {{ is_demo }};
  pm.dialogBackgroundColor = config.dialogColor;
  pm.dialogButtonBackgroundColor = config.dialogButtonColor;
  pm.hasServiceWorkers = ('serviceWorker' in navigator);
  pm.isChrome = pm.checkIfChrome();
  pm.isFirefox = pm.checkIfFirefox();
  pm.isHttps = (document.location.protocol == "https:"); 
  pm.isNotWordpress = config.isNotWordpress;
  pm.isPopUp = (window.opener != undefined);
  pm.isSafari = pm.checkIfSafari();
  pm.isSubFrame = (window.top != window);
  pm.os = pm.getOS(); 
  pm.safariHost = "https://www.getpushmonkey.com";   
  pm.safariEndpointURL = pm.safariHost + "/push";
  pm.safariWebPushID = "web.com.pushmonkey." + pm.accountKey;
  pm.sdkHost = "https://{{ subdomain }}.getpushmonkey.com";
  pm.segmentationEnabled = config.segmentation;
  pm.serviceWorker = './service-worker.js';  
  pm.serviceWorkerLocal = './service-worker-'+pm.accountKey+'.php';
  pm.serviceWorkersSupportNotifications = ("undefined" != typeof ServiceWorkerRegistration && 'showNotification' in ServiceWorkerRegistration.prototype && 'PushManager' in window);
  pm.windowSrc = pm.sdkHost + "/" + config.accountKey + "/register-service-worker";  
};
(function(config) {

  if ("object" !== typeof config) {

    console.log("Push Monkey: Missing configuration");
  } else {

    window._pushmonkey = new PushMonkey(config);
    window._pushmonkey.fireUp();
  }
})(window.pushMonkeyConfig);