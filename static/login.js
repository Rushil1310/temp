async function didILogin() {
    resp = await fetch("/me");
    if(resp.ok) window.location.href = "/lobby";
}

didILogin();