# Profile assets

Prepared for `divyanshu-dugar/divyanshu-dugar`, starting from commit
`b1140b18b85187637b26486fde80410e095ce6ce` on 2026-11-20.

## Installation

Copy this package's `README.md`, `assets/`, `scripts/`, and `.github/` into the
root of your profile repository, keeping existing unrelated files. Commit the
changes to `main`. The README uses repository-relative image paths, so both the
README and assets must be committed together.

The README uses the versioned assets in this repository.

## Design

- `hero.gif` is the README's animated hero: 60 frames, 20 fps, a seamless
  three-second loop. It preserves the reference's `#0d1117` background,
  contribution greens, rotating fade, and 40 ms column stagger, adapted to
  Divyanshu's longer name. Pixel glyphs and geometry are newly generated.
- `hero.svg` is the vector version of the animation. To use it, change the
  README image source from `hero.gif` to `hero.svg`.
- `hero-static.svg` is selected when the browser requests reduced motion.
- `whoami.svg` contains the terminal introduction and a blinking cursor.
- `tech-stack.svg` contains four columns, vertical dividers, restrained icon
  motion, and a testing row. Its animation respects reduced motion.
- Contact buttons are individual images, so each whole button is clickable.
- All custom images are self-contained; no remote fonts, scripts, or icon
  services are needed at render time. Existing GitHub, LeetCode and profile
  view widgets still depend on their original external services.

## NeetCode updates

The card reads the same unauthenticated `getProfileByHandle` request used by
the public NeetCode profile. It displays unique solved counts from
`ncAllDifficultyStats`, **not** the misleading `totalSolvedOrSubmissions`
activity count. At preparation time these were 14 solved and 22 activities.

The workflow refreshes once daily at 12:17 UTC, runs when its implementation
changes on `main`, and supports **Run workflow** in GitHub Actions. Schedules may run late. GitHub can suspend scheduled
workflows in inactive public repositories. The footer records the actual
fetch date. No personal API keys or login credentials are required.

NeetCode's endpoint is undocumented and can change. Unexpected, missing, or
invalid data fails the update before replacing the last successful card;
the workflow reports a failure instead of publishing invented zeroes.

## Rebuild

With Python 3:

```sh
python3 scripts/build_assets.py
python3 scripts/update_neetcode.py
```

To rebuild the GIF, install Pillow and use the included optional script.
Its font constant can be adjusted for another operating system.

```sh
python3 scripts/render_hero_gif.py
```

## Sources and credits

- Hero visual reference: https://github.com/kairothq
- Skills and current profile: https://www.divyanshu-dugar.me/
- NeetCode: https://neetcode.io/user/EternalGenin455
- Technology logos: https://github.com/devicons/devicon (MIT)
- Monochrome brand logos: https://github.com/simple-icons/simple-icons (CC0;
  some brand marks from release 11.0.0). Brand trademarks belong to their
  respective owners.
- Generic terminal, storage, compute, RAG and agent symbols are original
  line drawings. The NeetCode contact symbol is a custom code icon.

See the bundled Devicon license for redistributed icon attribution.
