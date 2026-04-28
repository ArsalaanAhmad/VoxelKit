---
description: How to report issues in VoxelKit — why issues matter and what to include.
---

# Reporting Issues

Issues are genuinely valuable — even ones that don't get fixed immediately. They tell me (and anyone who finds the project later) that something is broken or confusing, and they create a paper trail for solutions.

If something isn't working, or something is unclear in the docs, please open an issue. You don't need to be certain it's a bug. "I expected X but got Y" is enough.

---

## Where to open one

[github.com/ArsalaanAhmad/VoxelKit/issues](https://github.com/ArsalaanAhmad/VoxelKit/issues) → **New issue**

---

## What to include

The more context you give, the faster it gets resolved. Here's what helps:

**1. What you expected to happen**

Even one sentence: "I expected `report_file` to return a dict with a `warnings` key."

**2. What actually happened**

The actual output, error message, or behaviour you got. Copy-paste the exact error if there is one.

**3. Steps to reproduce**

The shortest sequence of commands or code that triggers the problem. If you can reduce it to three lines, do that.

**4. Your environment**

```
OS: Windows 11 / macOS 14 / Ubuntu 22.04
Python version: 3.11.2
VoxelKit version: 0.1.5  (run: pip show voxelkit)
```

**5. A sample file (if relevant)**

If the bug only happens with a specific file, attaching a minimal version of it (or describing its structure) saves a lot of back-and-forth.

---

## Types of issues worth opening

- **Bug reports** — something crashes, returns wrong results, or behaves unexpectedly
- **Documentation issues** — something is confusing, missing, or wrong in the docs
- **Feature requests** — a format you'd like supported, a flag you'd find useful
- **Questions** — if you're unsure whether something is a bug or expected behaviour, just ask

---

## You don't need to be certain

"I'm not sure if this is a bug but..." is a perfectly valid way to start an issue. The worst case is that it turns out to be expected behaviour and gets documented better because of the question. That's still a win.
