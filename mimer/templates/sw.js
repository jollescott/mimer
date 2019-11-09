self.addEventListener('push', function (event) {
    const eventInfo = event.data.text();
    const data = JSON.parse(eventInfo);
    const head = data.head || 'New Notification 🕺🕺';
    const body = data.body || 'This is default content. Your notification didn\'t have one 🙄🙄';

    event.waitUntil(self.registration.showNotification(head, {
        body: body,
        icon: 'https://upload.wikimedia.org/wikipedia/commons/0/09/Flag_of_Greenland.svg'
    }));
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    event.waitUntil(
        clients.openWindow("https://frogor.joellinder.dev/train")
    );
});