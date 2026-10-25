# Paper Stack / design A

This branch implements the selected light monochrome design in the existing Flask app. It does not change nginx, service configuration, SSH behavior, admin authentication, or database/storage formats. The existing admin editor continues to control `content.json` and `projects.json`.

## Changed behavior

- PCB trace background; existing profile image; server-rendered experience, biography, skills and project cards.
- Software-first positioning and project ordering, while retaining hardware experience. Project JSON itself is not reordered or rewritten.
- Isometric layers sit 5–9 SVG units apart at rest. Fine-pointer hover separates them by roughly 80–95 SVG units. The top layer travels 141 SVG units between states (scaled to the viewport). Transitions last 850 ms.
- Moving the mouse away collapses the assembly. Click/Enter/Space pins it open; click again to unpin. Touch users tap to toggle. Reduced-motion users get instant state changes instead of animated movement.
- Original oneko sprite and animation retained, including attribution. Absolute `data-cat` asset paths also work on `/fa/more`. Storage failures or corrupted saved cat state no longer break the animation. On the compact homepage the cat starts below the header, not over its buttons. It ignores pointer events.
- Existing light/dark preference, English/Persian routes, `/more`, `/fa/more`, `/api/projects` and the 418 easter egg remain available. Homepage content is usable without JavaScript.
- Admin-edited content is escaped. Project links are restricted to HTTP(S) in the new homepage renderer.

## Local verification

Use the repository's existing dependencies, then run:

```sh
python -m unittest discover -s tests -v
flask --app app run --host 127.0.0.1 --port 5055
```

Seven Flask regression tests cover routes, EN/FA server-rendered content, original cat inclusion, software-first projection without data mutation, escaping/unsafe links, empty projects, and existing admin authentication.

Browser checks completed in Chromium at 1440 px and 390 px: compact/expanded/return animation, click pin, touch and keyboard toggles, reduced motion, cat pointer tracking, invalid localStorage, filters, theme persistence, SSH clipboard copy, no-JavaScript content, loaded assets and horizontal overflow. Visual review includes light/dark, EN/FA, mobile, desktop, expanded assembly and both existing setup pages.

## Deployment / rollback

Review and merge the pull request into `master`, then deploy with the site's existing release procedure. No service credentials or live-server access were used in preparing this branch. The live website is not changed by the branch/PR itself. Keep the existing `static/profile.jpg`, `static/oneko.gif` and other original assets.

The attached changed-files ZIP is an overlay for an existing checkout, not a replacement for the full repository. Back up locally edited `content.json` before applying it. Rollback by reverting this commit (including the content overrides) and redeploying with the same existing process.
