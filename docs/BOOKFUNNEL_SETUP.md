# BookFunnel → WooCommerce Delivery Setup

How Blackbird (and later Borogrove) delivers ebooks on direct-sale orders via BookFunnel. PUB-13.

## How it works

BookFunnel matches each WooCommerce purchase to a BookFunnel **delivery action** by **SKU**. When a reader buys, BookFunnel emails them a unique, watermarked download link and handles all reader support. WooCommerce itself does **not** deliver the file.

**The match key is the SKU, and it must match exactly — including capitalization.**

## Requirements (already confirmed)

- BookFunnel plan **Mid-List Author or above** (covers the WooCommerce sales integration). ✅ Confirmed 2026-06-28.
- Self-hosted WordPress (✅ blackbirdpublishing.com on WP Engine).

## Woo side — DONE by Rookwood (2026-06-28)

Each ebook variation has been set to:
- **Virtual = on, Downloadable = OFF.** (If Downloadable is on, WooCommerce tries to deliver the file itself and bypasses BookFunnel.)
- A unique **SKU** (below).

## Jamie side — to do in the BookFunnel + WordPress dashboards

1. **Install the plugin.** WordPress dashboard → Plugins → Add New → search **"BookFunnel"** → Install → Activate.
2. **Connect.** Log into BookFunnel in the same browser first (the correct account if you have multiples). Then WooCommerce → BookFunnel → **Connect to BookFunnel**. It auto-links the logged-in account.
3. **Upload each book to BookFunnel** (if not already there): upload the EPUB (BookFunnel converts/watermarks; add a PDF too if you want PDF delivery).
4. **Create one delivery action per book** in the BookFunnel **Sales** dashboard:
   - Name it (e.g. the book title).
   - Select the book file(s) to deliver.
   - Delivery timing: **Immediately**.
   - Platform: **WooCommerce**.
   - **SKU: paste the exact SKU from the table below** (case-sensitive).
   - Optional: product permalink + a custom delivery email.
5. Save. The next matching sale auto-delivers.

## SKU mapping (Woo ↔ BookFunnel)

Mirror these exactly in each BookFunnel delivery action.

| Title | Type | Woo product | Variation | **SKU** |
|---|---|---|---|---|
| With Perfect Clarity | novel | 5775 | 5776 | `BB-WPCLARITY-EB` |
| The Gate | short story | 5777 | 5778 | `BB-GATE-EB` |
| And Never Return to the Sea | short story | 5779 | 5780 | `BB-NEVERRETURN-EB` |
| To Speak to the Gods | short story | 5781 | 5782 | `BB-SPEAKGODS-EB` |
| Be Nice to Statues | short story | 5783 | 5784 | `BB-STATUES-EB` |
| The Porta Alchemica | short story | 5786 | 5787 | `BB-PORTA-EB` |
| Dance Hall Days | short story | 5788 | 5789 | `BB-DANCEHALL-EB` |
| The Center of the Maze | short story | 5790 | 5791 | `BB-MAZE-EB` |
| A Better Place | short story | 5792 | 5793 | `BB-BETTERPLACE-EB` |
| A Different Turn | short story | 5794 | 5795 | `BB-DIFFTURN-EB` |
| When the Wind Blows | short story | 5796 | 5797 | `BB-WINDBLOWS-EB` |
| The Tommys | short story | 5798 | 5799 | `BB-TOMMYS-EB` |
| Diamond Betty | short story | 5800 | 5801 | `BB-DIAMONDBETTY-EB` |
| Inside a Fairy Tale | short story | 5802 | 5803 | `BB-FAIRYTALE-EB` |
| Entangled by Midsummer | novel | 5804 | 5805 | `BB-ENTANGLED-EB` |
| Bewitchery | novelette | 5806 | 5807 | `BB-BEWITCHERY-EB` |
| Bundle Up! 2nd Edition | non-fiction | 5808 | 5809 | `BB-BUNDLEUP-EB` |

## Verify (test order)

After connecting and creating the delivery actions, run one real end-to-end test (PUB-20): buy a published test product, confirm the BookFunnel email + download link arrive, and that the BookFunnel **delivery log** shows the order. BookFunnel supports refund/cancellation, a delivery log, and auto-retry if a notification fails.

## SKU convention (for new titles)

`BB-<SHORTNAME>-EB` for Blackbird ebooks (`-PB` reserved for the Phase-2 paperback variation). Borogrove will use `BG-<SHORTNAME>-EB`. Keep them unique and stable — changing a SKU later breaks the BookFunnel match.

## Sources
- [BookFunnel: Sell With WooCommerce and We'll Deliver](https://authors.bookfunnel.com/help/setup-woocommerce/)
- [BookFunnel plugin announcement](https://blog.bookfunnel.com/2026/selling-with-woocommerce-just-got-better-introducing-the-bookfunnel-plugin/)
