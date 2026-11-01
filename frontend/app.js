"use strict";

/* ---------- helpers: bytes <-> base64url ---------- */
function toB64url(bytes) {
  let bin = "";
  for (const b of bytes) bin += String.fromCharCode(b);
  return btoa(bin).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function fromB64url(str) {
  let s = str.replace(/-/g, "+").replace(/_/g, "/");
  while (s.length % 4) s += "=";
  return Uint8Array.from(atob(s), (c) => c.charCodeAt(0));
}

/* ---------- crypto: AES-GCM 256 via WebCrypto ---------- */
const MAX_CIPHERTEXT_LEN = 20000; // keep in sync with backend max_ciphertext_length

async function encryptText(plaintext) {
  // 1. fresh random 256-bit key for every message
  const key = await crypto.subtle.generateKey({ name: "AES-GCM", length: 256 }, true, ["encrypt"]);
  // 2. fresh random 12-byte IV; never reuse an IV with the same key
  const iv = crypto.getRandomValues(new Uint8Array(12));
  // 3. encrypt (GCM also adds an authentication tag, so tampering is detected)
  const data = new TextEncoder().encode(plaintext);
  const encrypted = new Uint8Array(await crypto.subtle.encrypt({ name: "AES-GCM", iv }, key, data));
  // 4. payload = iv + ciphertext, so the receiver can split them again
  const payload = new Uint8Array(iv.length + encrypted.length);
  payload.set(iv, 0);
  payload.set(encrypted, iv.length);
  // 5. export the raw key so it can go in the URL #fragment
  const rawKey = new Uint8Array(await crypto.subtle.exportKey("raw", key));
  return { ciphertext: toB64url(payload), key: toB64url(rawKey) };
}

async function decryptText(ciphertextB64, keyB64) {
  const rawKey = fromB64url(keyB64);
  const key = await crypto.subtle.importKey("raw", rawKey, { name: "AES-GCM" }, false, ["decrypt"]);
  const payload = fromB64url(ciphertextB64);
  const iv = payload.slice(0, 12);
  const body = payload.slice(12);
  const plain = await crypto.subtle.decrypt({ name: "AES-GCM", iv }, key, body); // throws if key is wrong or data was changed
  return new TextDecoder().decode(plain);
}

/* ---------- UI helpers ---------- */
const $ = (id) => document.getElementById(id);

function showError(msg) {
  const el = $("error");
  el.textContent = msg;
  el.hidden = false;
}

function clearError() {
  $("error").hidden = true;
}

/* ---------- create page ---------- */
function initCreate() {
  const textarea = $("plaintext");
  const btn = $("encrypt-btn");

  textarea.addEventListener("input", () => {
    $("count").textContent = textarea.value.length + " / 10000";
  });

  btn.addEventListener("click", async () => {
    clearError();
    const text = textarea.value;
    if (!text.trim()) return showError("Type a message first.");

    btn.disabled = true;
    try {
      const { ciphertext, key } = await encryptText(text);
      if (ciphertext.length > MAX_CIPHERTEXT_LEN) {
        return showError("Message is too long after encryption. Shorten it a little.");
      }

      const res = await fetch("/message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ciphertext }),
      });
      if (!res.ok) return showError("Server rejected the message (status " + res.status + ").");

      const { id } = await res.json();
      // the key goes after '#', so the browser never sends it to the server
      $("link").value = location.origin + "/view.html?id=" + encodeURIComponent(id) + "#" + key;
      $("result").hidden = false;
      textarea.value = "";
      $("count").textContent = "0 / 10000";
    } catch (err) {
      showError("Something went wrong while encrypting. Is this page on https or localhost?");
    } finally {
      btn.disabled = false;
    }
  });

  $("copy-btn").addEventListener("click", async () => {
    await navigator.clipboard.writeText($("link").value);
    $("copy-btn").textContent = "Copied";
    setTimeout(() => ($("copy-btn").textContent = "Copy link"), 1500);
  });
}

/* ---------- view page ---------- */
function initView() {
  const id = new URLSearchParams(location.search).get("id");
  const key = location.hash.slice(1);
  const btn = $("reveal-btn");

  if (!id || !key) {
    $("gate").hidden = true;
    return showError("This link is incomplete. Ask the sender for the full link, including the part after #.");
  }

  // Nothing is fetched on page load. Link-preview bots open the page but never click,
  // so they can't use up the message.
  btn.addEventListener("click", async () => {
    clearError();
    btn.disabled = true;
    try {
      const res = await fetch("/message/" + encodeURIComponent(id));
      if (res.status === 404) {
        $("gate").hidden = true;
        return showError("This message doesn't exist, has expired, or was already opened.");
      }
      if (!res.ok) return showError("Server error (status " + res.status + "). Try again.");

      const { ciphertext } = await res.json();
      let text;
      try {
        text = await decryptText(ciphertext, key);
      } catch (e) {
        $("gate").hidden = true;
        return showError("Could not decrypt. The key in the link is wrong or damaged. The message is already deleted.");
      }

      $("message-text").textContent = text; // textContent, never innerHTML (prevents XSS)
      $("gate").hidden = true;
      $("output").hidden = false;
      history.replaceState(null, "", location.pathname); // remove the key from the address bar
    } catch (err) {
      showError("Network error. Check your connection and try again.");
    } finally {
      btn.disabled = false;
    }
  });
}

const page = document.body.dataset.page;
if (page === "create") initCreate();
if (page === "view") initView();


