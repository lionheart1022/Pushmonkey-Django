try {
    window.pushMonkeyConfig = {
        accountKey: "{{ account_key }}",
        debug: 0,
        dialogColor: "{{ dialog_color }}",
        dialogButtonColor: "{{ button_color }}"
    }
    var container = document.body ? document.body : document.head;
    var script = document.createElement("script");
    script.id="PushMonkeySDK",
    script.src="//www.getpushmonkey.com/sdk/sdk.js",
    container.appendChild(script)
} catch(err) {
}