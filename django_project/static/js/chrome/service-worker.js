'use strict';

var pushMonkeySWConfig = {
    version: 1,
    logging: true, // TODO: set to false when live
    host: "https://dev-pushmonkeymowow.rhcloud.com" // TODO: add live
};

self.addEventListener('push', function(event) {

  if (pushMonkeySWConfig.logging) console.log('Received a push message: ', event);
  event.waitUntil(self.registration.pushManager.getSubscription().then(function(subscription) {

    var endpointSections = subscription.endpoint.split('/');
    var subscriptionId = endpointSections[endpointSections.length - 1];
    var url = pushMonkeySWConfig.host + "/push/v1/notifs/" + self.accountKey;
    if (pushMonkeySWConfig.logging) console.log(url);
    return fetch(url).then(function(response) {

      return response.json().then(function(json) {

        if (pushMonkeySWConfig.logging) console.log(json);
        var promises = [];
        promises.push(showNotification(json.title, {

          body: json.body,
          icon: json.icon,
          tag: json.id
        }));
        return Promise.all(promises);
      });
    });
  }));
});

self.addEventListener('notificationclick', function(event) {

  console.log('On notification click: ', event.notification.tag);
  // Android doesn’t close the notification when you click on it
  // See: http://crbug.com/463146
  event.notification.close();
  // This looks to see if the current is already open and
  // focuses if it is
  event.waitUntil(clients.matchAll({
    type: "window"
  }).then(function(clientList) {
    for (var i = 0; i < clientList.length; i++) {
      var client = clientList[i];
      if (client.url == '/' && 'focus' in client)
        return client.focus();
    }
    if (clients.openWindow)
      return clients.openWindow(pushMonkeySWConfig.host + '/stats/track_open/' + event.notification.tag);
  }));
});

function showNotification(title, options) {

  self.registration.showNotification(title, options);
}
