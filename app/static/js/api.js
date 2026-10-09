
export const api = {
  async request(method, url, body) {
    const opts = {
      method,
      headers: { "Content-Type": "application/json" },
      credentials: "include",
    };
    if (body !== undefined) opts.body = JSON.stringify(body);

    const res = await fetch(url, opts);
    let data = null;
    try { data = await res.json(); } catch (e) { /* empty body, e.g. 204 */ }

    if (!res.ok) {
      const message = (data && data.error) || `Request failed (${res.status})`;
      throw new Error(message);
    }
    return data;
  },
  get(url) { return this.request("GET", url); },
  post(url, body) { return this.request("POST", url, body); },
  put(url, body) { return this.request("PUT", url, body); },


  async upload(url, formData) {
    const res = await fetch(url, { method: "POST", body: formData, credentials: "include" });
    const data = await res.json().catch(() => null);
    if (!res.ok) throw new Error((data && data.error) || `Upload failed (${res.status})`);
    return data;
  },
};
