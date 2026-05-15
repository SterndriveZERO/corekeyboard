# -*- coding: utf-8 -*-
"""Strip header chrome (search, cart, locale, account, mega menu) and footer/filters from templates/index.html."""
import re
from pathlib import Path

PATH = Path(__file__).resolve().parent / "templates" / "index.html"

CONTACT_NAV = """<nav class="header__inline-menu">
  <ul class="list-menu list-menu--inline" role="list">
    <li><a href="#" class="header__menu-item list-menu__item link link--text focus-inset"><span>Contact Us</span></a></li>
  </ul>
</nav>"""


def main():
    s = PATH.read_text(encoding="utf-8")

    # Cart drawer (entire off-canvas cart)
    s = re.sub(r"<cart-drawer\b[\s\S]*?</cart-drawer>\s*", "", s, count=1)

    # Desktop header search (inside header__icons)
    s = re.sub(
        r"\n\s*<div class=\"header__search\">[\s\S]*?\n\s*</div>\n\n\n\s*\n\s*<div class=\"header-toolbar \"",
        '\n          <div class="header-toolbar "',
        s,
        count=1,
    )

    # Cart icon in toolbar
    s = re.sub(
        r'<a href="#" class="header__icon header__icon--cart link focus-inset" id="cart-icon-bubble">[\s\S]*?</a>\s*\n\s*\n',
        "",
        s,
        count=1,
    )

    # Country + language + Geolizr currency block (through closing div before account)
    s = re.sub(
        r'<div class="desktop-localization-wrapper">[\s\S]*?(?=<div class="header__icon header__icon--account link focus-inset">)',
        "",
        s,
        count=1,
    )

    # Account dropdown + its script (and orphan drawer CSS link that sat before <header-drawer>)
    s = re.sub(
        r'<div class="header__icon header__icon--account link focus-inset">[\s\S]*?</script>\s*(?:\n\s*<link href="//redragonshop\.com/cdn/shop/t/209/assets/component-header-drawer\.css[^>]*>\s*)?',
        "",
        s,
        count=1,
    )

    # Mobile menu drawer (full duplicate nav)
    s = re.sub(r"<header-drawer\b[\s\S]*?</header-drawer>\s*", "", s, count=1)

    # Main nav → Contact Us only
    s = re.sub(r'<nav class="header__inline-menu">[\s\S]*?</nav>', CONTACT_NAV, s, count=1)

    # Mobile search under header
    s = re.sub(
        r"\n\s*<div class=\"header-search-mb\">[\s\S]*?\n\s*</div>\n\n\n\s*</div></header>",
        "\n    </div></header>",
        s,
        count=1,
    )

    # Toolbar cleanup (empty or only leftover header-drawer stylesheet link)
    s = re.sub(
        r'<div class="header-toolbar ">\s*(?:<link href="//redragonshop\.com/cdn/shop/t/209/assets/component-header-drawer\.css[^>]*>\s*)?\s*</div>\s*',
        "",
        s,
        count=1,
    )

    # If toolbar was removed but icons/middle/first-row closed too early, keep nav inside first row
    s = re.sub(
        r'(</div>\s*</div>\s*</div>)\s*\n\s*\n(<nav class="header__inline-menu">)',
        r"</div>\n      </div>\n\n\2",
        s,
        count=1,
    )

    # Sort row (facet vertical sort)
    s = re.sub(
        r'<facet-filters-form class="facets facets-vertical-sort page-width small-hide">[\s\S]*?</facet-filters-form>\s*',
        "",
        s,
        count=1,
    )

    # Sidebar + mobile facets: from facets-vertical opening through </aside> before product grid
    s = re.sub(
        r'<div class=" facets-vertical page-width">\s*'
        r'<link href="//redragonshop\.com/cdn/shop/t/209/assets/component-facets\.css[^>]*>\s*'
        r'<script src="//redragonshop\.com/cdn/shop/t/209/assets/facets\.js[^>]*></script>\s*'
        r'<aside\b[\s\S]*?</aside>\s*\n\s*\n\s*',
        '<div class=" facets-vertical page-width">\n      ',
        s,
        count=1,
    )

    # Active facet chips above product grid
    s = re.sub(
        r'<div class="active-facets active-facets-desktop">[\s\S]*?</div>\s*\n<div\n\s*class="collection"',
        '<div\n            class="collection"',
        s,
        count=1,
    )

    # Footer section group
    s = re.sub(
        r"\s*<!-- BEGIN sections: footer-group -->[\s\S]*?<!-- END sections: footer-group -->\s*",
        "\n",
        s,
        count=1,
    )

    PATH.write_text(s, encoding="utf-8")
    print(f"Updated {PATH} ({len(s)} bytes)")


if __name__ == "__main__":
    main()
