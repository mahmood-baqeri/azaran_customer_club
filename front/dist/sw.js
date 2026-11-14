self.addEventListener("push", function(event) {
  let data = { title: "Notification", body: "You have a message" };
  if (event.data) {
    try {
      data = event.data.json();
    } catch (e) {
      data = { title: "Notification", body: event.data.text() };
    }
  }
  const title = data.title || "Notification";
  const options = {
    body: data.body || "",
    icon: "/assets/logo.png",
    badge: "/assets/logo.png"
  };
  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener("notificationclick", function(event) {
  event.notification.close();
  event.waitUntil(
    clients.matchAll({ type: "window" }).then(function(clientList) {
      if (clientList.length > 0) {
        let client = clientList[0];
        return client.focus();
      }
      return clients.openWindow("/");
    })
  );
});
