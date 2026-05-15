# -*- coding: utf-8 -*-
"""
Restore templates/index.html from _ref_fetch.html, then strip third-party ads/tracking
and neutralize <a href> / form action so the file stays a single static page.
"""
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REF = ROOT / "_ref_fetch.html"
OUT = ROOT / "templates" / "index.html"


def rewrite_tags(html: str, tag: str, attr: str, repl_value: str) -> str:
    """Rewrite attr=... inside opening tags <tag ...> (not nested, HTML-ish)."""
    out = []
    pos = 0
    low = html.lower()
    open_pat = f"<{tag.lower()}"
    while True:
        i = low.find(open_pat, pos)
        if i == -1:
            out.append(html[pos:])
            break
        out.append(html[pos:i])
        gt = html.find(">", i)
        if gt == -1:
            out.append(html[i:])
            break
        chunk = html[i : gt + 1]
        # only opening tags, not </a>
        if chunk.startswith("</"):
            out.append(chunk)
            pos = gt + 1
            continue
        newc = chunk
        newc = re.sub(
            rf"(?i){attr}\s*=\s*\"https://redragonshop\.com[^\"]*\"",
            f'{attr}="{repl_value}"',
            newc,
        )
        newc = re.sub(
            rf"(?i){attr}\s*=\s*'https://redragonshop\.com[^']*'",
            f"{attr}='{repl_value}'",
            newc,
        )
        newc = re.sub(
            rf"(?i){attr}\s*=\s*\"http://redragonshop\.com[^\"]*\"",
            f'{attr}="{repl_value}"',
            newc,
        )
        newc = re.sub(
            rf"(?i){attr}\s*=\s*\"//redragonshop\.com[^\"]*\"",
            f'{attr}="{repl_value}"',
            newc,
        )
        newc = re.sub(
            rf"(?i){attr}\s*=\s*'//redragonshop\.com[^']*'",
            f"{attr}='{repl_value}'",
            newc,
        )
        newc = re.sub(
            rf"(?i){attr}\s*=\s*\"https://redragonshop\.myshopify\.com[^\"]*\"",
            f'{attr}="{repl_value}"',
            newc,
        )
        newc = re.sub(
            rf"(?i){attr}\s*=\s*\"/[^\"]*\"",
            f'{attr}="{repl_value}"',
            newc,
        )
        newc = re.sub(
            rf"(?i){attr}\s*=\s*'/[^']*'",
            f"{attr}='{repl_value}'",
            newc,
        )
        out.append(newc)
        pos = gt + 1
    return "".join(out)


def ensure_reference_html() -> None:
    if REF.is_file():
        return
    import urllib.request

    url = "https://redragonshop.com/collections/redragon-mechanical-keyboard"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        REF.write_text(resp.read().decode("utf-8", errors="replace"), encoding="utf-8")
    print(f"Downloaded reference HTML to {REF}")


def main():
    ensure_reference_html()
    shutil.copyfile(REF, OUT)
    s = OUT.read_text(encoding="utf-8")

    # Minimal Geolizr stub (head library removed; body still references Geolizr)
    geolizr_stub = """<script>
window.Geolizr=window.Geolizr||{
  version:20200327,
  currency_widget_enabled:true,
  shopifyFormatMoneySet:false,
  config:function(){},
  switchCurrency:function(){},
  appendShopifyFormatMoney:function(m){return m;},
  addEventListener:function(n,cb){if(cb)setTimeout(function(){try{cb(window.jQuery||window.$)}catch(e){}},0);},
  addSystemEventListener:function(n,cb){if(cb)setTimeout(function(){try{cb()}catch(e){}},0);},
  init:function(cb){if(cb)setTimeout(function(){try{cb(window.jQuery||window.$)}catch(e){}},0);},
  initWrappers:function(){},
  getGeoData:function(cb){if(cb)cb({});}
};
</script>
"""
    s = s.replace("<head>", "<head>\n" + geolizr_stub, 1)

    # --- Geolizr ---
    s = re.sub(
        r'\s*<script async src="//redragonshop\.com/cdn/shop/t/209/assets/geolizr-lib\.js[^"]*"[^>]*></script>\s*'
        r"<script>[\s\S]*?</style>\s*",
        "\n",
        s,
        count=1,
    )

    # --- Klaviyo (head + app embed) ---
    s = re.sub(
        r'<script async type="text/javascript" src="https://static\.klaviyo\.com/onsite/js/klaviyo\.js[^"]*"></script>\s*',
        "",
        s,
        count=1,
    )
    s = re.sub(
        r"<!-- END app block --><!-- BEGIN app block: shopify://apps/klaviyo-email-marketing-sms/blocks/klaviyo-onsite-embed/[\s\S]*?<!-- END app block -->",
        "<!-- END app block -->",
        s,
        count=1,
    )

    # --- dataLayer stub ---
    s = re.sub(
        r"<script type=\"text/javascript\">\s*window\.dataLayer = window\.dataLayer \|\| \[\];[\s\S]*?appStart\(\);\s*</script>\s*",
        "",
        s,
        count=1,
    )

    # --- Smile.io ---
    s = re.sub(
        r'<div\s+class="smile-shopify-init"[\s\S]*?</div>\s*',
        "",
        s,
        count=1,
    )

    # --- Bing UET ---
    s = re.sub(
        r"<script defer>\s*"
        r"\(function\(w,d,t,r,u\)\{var f,n,i;w\[u\][\s\S]*?</script>\s*",
        "",
        s,
        count=1,
    )

    # --- Google merchant badge ---
    s = re.sub(
        r'<script src="//apis\.google\.com/js/platform\.js\?onload=renderBadge" defer></script>\s*'
        r"<script defer>[\s\S]*?window\.gapi\.ratingbadge\.render[\s\S]*?</script>\s*",
        "",
        s,
        count=1,
    )

    # --- Hotjar ---
    s = re.sub(
        r"<!-- Hotjar Tracking Code[^>]*-->[\s\S]*?<!-- end -->",
        "<!-- end -->",
        s,
        count=1,
    )

    # --- Third-party Shopify app script bundle on load ---
    s = re.sub(r"var urls = \[[^\]]*\];", "var urls = [];", s, count=1)

    # --- Selly / CloudFront promotion loader (pattern varies in saved HTML) ---
    s = re.sub(
        r"<!-- BEGIN app block: shopify://apps/selly-promotion-pricing[\s\S]*?<!-- END app block -->",
        "",
        s,
        count=1,
    )

    # --- Web Pixels Manager (Meta, Google Ads, Bing, affiliates, etc.) ---
    s = re.sub(
        r'<script id="web-pixels-manager-setup">[\s\S]*?</script>\s*(?=<script>\s*\n  window\.ShopifyAnalytics)',
        "",
        s,
        count=1,
    )

    # --- PushOwl extension script tag ---
    s = re.sub(
        r'<script src="https://cdn\.shopify\.com/extensions/[^"]*pushowl-shopify\.js[^"]*"[^>]*></script>\s*',
        "",
        s,
        count=1,
    )

    # --- Firework shoppable video / live helper (third-party embed) ---
    s = re.sub(
        r"<!-- BEGIN app block: shopify://apps/firework-shoppable-video-ugc[\s\S]*?<!-- END app block -->",
        "",
        s,
        count=1,
    )

    # --- Smile.io rewards loader (Shopify extension) ---
    s = re.sub(
        r'<script src="https://cdn\.shopify\.com/extensions/[^"]*smile-loader\.js[^"]*"[^>]*></script>\s*',
        "",
        s,
        count=1,
    )

    # --- Shop.app checkout preloads ---
    s = re.sub(
        r'<script async="async" src="/checkouts/internal/preloads\.js[^"]*"></script>\s*',
        "",
        s,
        count=1,
    )
    s = re.sub(
        r'<script async="async" src="https://shop\.app/checkouts/internal/preloads\.js[^"]*"[^>]*></script>\s*',
        "",
        s,
        count=1,
    )

    # --- Shop Pay / Sign-in cart sync (shop.app redirects) ---
    s = re.sub(
        r'<script defer="defer" async type="module" src="//redragonshop\.com/cdn/shopifycloud/shop-js/modules/v2/loader\.init-shop-cart-sync[^"]*"></script>\s*'
        r"<script type=\"module\">[\s\S]*?initShopCartSync[\s\S]*?</script>\s*",
        "",
        s,
        count=1,
    )

    # --- Monorail abandonment beacon ---
    s = re.sub(
        r'<link href="https://monorail-edge\.shopifysvc\.com" rel="dns-prefetch">\s*'
        r"<script>\(function\(\)\{if \(\"sendBeacon\" in navigator[\s\S]*?</script>\s*",
        "",
        s,
        count=1,
    )

    # --- Single-page navigation: anchors + forms only ---
    s = rewrite_tags(s, "a", "href", "#")
    s = rewrite_tags(s, "form", "action", "#")
    # Remaining external links (social, account.* subdomain, etc.)
    s = re.sub(
        r'(<a\s[^>]*?)href\s*=\s*"https://[^"]*"',
        r'\1href="#"',
        s,
        flags=re.I,
    )
    s = re.sub(
        r"(<a\s[^>]*?)href\s*=\s*'https://[^']*'",
        r"\1href='#'",
        s,
        flags=re.I,
    )
    s = re.sub(
        r'(<a\s[^>]*?)href\s*=\s*"http://[^"]*"',
        r'\1href="#"',
        s,
        flags=re.I,
    )

    s = re.sub(
        r'<link rel="canonical" href="https://redragonshop\.com[^"]*">',
        '<link rel="canonical" href="#">',
        s,
        count=1,
    )
    s = re.sub(
        r'<link rel="alternate" hreflang="[^"]*" href="https://[^"]*">',
        "",
        s,
    )
    s = re.sub(
        r'<link rel="alternate" hreflang="[^"]*" href="https://[^"]*"\s*/>',
        "",
        s,
    )
    s = re.sub(
        r'<link rel="alternate" type="application/json\+oembed" href="https://redragonshop\.com[^"]*">',
        "",
        s,
        count=1,
    )
    s = re.sub(
        r'<link rel="alternate" type="application/atom\+xml"[^>]*>',
        "",
        s,
        count=1,
    )

    OUT.write_text(s, encoding="utf-8")
    try:
        REF.unlink()
    except OSError:
        pass
    print(f"Wrote {OUT} ({len(s)} bytes)")


if __name__ == "__main__":
    main()
