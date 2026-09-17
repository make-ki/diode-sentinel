# Vendored front-end assets

These files are checked in on purpose: the dashboard runs on the receive side
of a data diode, where the host has no path to a CDN. Serving them from the
same stdlib HTTP server means the SOC view renders on an isolated enclave.

| File | Package | Version | Licence | Source |
|---|---|---|---|---|
| `daisyui.css` | daisyUI | 5.7.38 | MIT | `https://cdn.jsdelivr.net/npm/daisyui@5.7.38/daisyui.css` |
| `chart.umd.min.js` | Chart.js | 4.5.0 | MIT | `https://cdn.jsdelivr.net/npm/chart.js@4.5.0/dist/chart.umd.min.js` |

`daisyui.css` is the prebuilt stylesheet: base reset, every component class
(`badge`, `table`, `progress`, `btn`, `modal`, …) and the light/dark themes.
It needs no Tailwind build step -- there is no npm in this project. Only
Tailwind *utility* classes (`grid`, `p-4`, …) are absent, so layout lives in
`static/app.css` instead.

Refresh both with:

```bash
curl -sL https://cdn.jsdelivr.net/npm/daisyui@5.7.38/daisyui.css \
     -o static/vendor/daisyui.css
curl -sL https://cdn.jsdelivr.net/npm/chart.js@4.5.0/dist/chart.umd.min.js \
     -o static/vendor/chart.umd.min.js
```
