"""
Misleader -- a satirical clickbait popup that teaches you not to click on
shady ads. Runs in the background and pops up a fake "ad" every few minutes
at a random spot on your screen. If you click it, you get roasted (and
maybe taught a small lesson, or treated to a fake virus install screen).

Usage:
    python misleader.py            # background loop, popup every 2-7 min
    python misleader.py --demo     # fire one popup immediately and exit
    python misleader.py --fast     # popup every 10-25 sec (for testing)
    python misleader.py --min 5 --max 15   # custom interval in minutes
"""

import argparse
import random
import sys
import time
import tkinter as tk
from tkinter import font as tkfont


# --- Content library ---------------------------------------------------------
# Each entry: clickbait headline, accent color, and (roast, lesson) pair.

ADS = [
    {
        "headline": "Hot singles in your area want to meet YOU!",
        "subhead": "[Click here] -- 3 matches waiting!",
        "color": "#ff3b6b",
        "roast": "Buddy. They cheer the more the merrier.\n"
                 "There are no girls on the internet,\n"
                 "only viruses and the NSA.",
        "lesson": "Real dating apps never ambush you with a popup. "
                  "Unsolicited 'matches' are almost always malware droppers or scams.",
    },
    {
        "headline": "Congratulations! You are the 1,000,000th visitor!",
        "subhead": "Claim your FREE iPhone 47 Pro Max now!",
        "color": "#ffb300",
        "roast": "You're not the millionth anything.\n"
                 "You're the millionth person to fall for this.\n"
                 "Apple is on iPhone 19, dingus.",
        "lesson": "If a site claims you 'won' something out of nowhere, it's a phishing page. "
                  "Legit prizes never live behind a flashing banner.",
    },
    {
        "headline": "Your PC is infected with 47 viruses!",
        "subhead": "Microsoft (TM) Official Cleaner -- DOWNLOAD NOW",
        "color": "#1e7fff",
        "roast": "Microsoft does not put a popup on your screen.\n"
                 "Microsoft barely puts updates on your screen.\n"
                 "That little fake shield logo is held on with crayon.",
        "lesson": "Real antivirus tools don't beg through browser popups. "
                  "If a site says you're infected, you're being scammed -- not scanned.",
    },
    {
        "headline": "Doctors HATE this one weird trick!",
        "subhead": "Local mom loses 60lbs eating ONLY this fruit",
        "color": "#39c46e",
        "roast": "Doctors do not hate tricks. Doctors hate paperwork.\n"
                 "The 'local mom' is a stock photo named Linda\n"
                 "and Linda has never seen this website.",
        "lesson": "'One weird trick' headlines are an ad-network template "
                  "designed to harvest clicks for affiliate fraud and supplement scams.",
    },
    {
        "headline": "PRINCE NEEDS YOUR HELP! Reward: $14,500,000 USD",
        "subhead": "Wire small fee to release inheritance. Trustworthy!!",
        "color": "#a259ff",
        "roast": "If a prince had fourteen million dollars\n"
                 "he would not be emailing YOU, meatbag.\n"
                 "He'd be emailing a guy with a yacht.",
        "lesson": "Advance-fee fraud (a.k.a. '419 scams') has been running for 40 years "
                  "because it still works. Any 'send a small fee to receive a big sum' message is a scam.",
    },
    {
        "headline": "WARNING: Someone in your area searched your name",
        "subhead": "See who's looking you up >>",
        "color": "#e34c00",
        "roast": "Nobody is searching for you.\n"
                 "I say this with love.\n"
                 "Your mom googled you once in 2019. That's it.",
        "lesson": "These 'people search' ads are designed to scare you into a paid 'background check' "
                  "that just scrapes public data and sells your info onward.",
    },
    {
        "headline": "Your Netflix subscription has EXPIRED",
        "subhead": "Update payment info in the next 24h or lose access",
        "color": "#e50914",
        "roast": "Netflix would never give you 24 hours.\n"
                 "Netflix would cancel you mid-episode\n"
                 "of the show you actually like.",
        "lesson": "Urgency + 'verify your payment' is the #1 phishing pattern. "
                  "Always go to the service's website directly -- never click the link.",
    },
    {
        "headline": "She removed her makeup and you won't BELIEVE what happened",
        "subhead": "#7 will SHOCK you",
        "color": "#ff6fa8",
        "roast": "Number 7 will not shock you.\n"
                 "Number 7 is an ad for car insurance.\n"
                 "Numbers 1 through 6 were also ads for car insurance.",
        "lesson": "Listicle bait pages are 90% ad load by weight. "
                  "Many also fingerprint your browser the second the page loads.",
    },
    {
        "headline": "FREE Robux generator -- no human verification!",
        "subhead": "Works 2026! Just enter your password to claim",
        "color": "#00b06f",
        "roast": "If something asks for your password to GIVE you something,\n"
                 "it is not giving. It is taking.\n"
                 "Also -- 'no human verification' means 'no humans involved, just thieves.'",
        "lesson": "Account-credential phishing is the most common attack against kids and teens. "
                  "No legit game gives currency in exchange for your login.",
    },
    {
        "headline": "Single dad in your zip code makes $9,847/week from home",
        "subhead": "Click to learn his ONE secret",
        "color": "#0099a8",
        "roast": "His one secret is that he doesn't exist.\n"
                 "His second secret is that the 'course' is $499.\n"
                 "His third secret is that there is no course.",
        "lesson": "Work-from-home 'income' ads almost always funnel into "
                  "high-pressure info-product sales or pyramid schemes.",
    },
    {
        "headline": "ALERT: Your browser is out of date!",
        "subhead": "Click here to install the latest secure version",
        "color": "#ff8800",
        "roast": "Your browser updates itself in the background.\n"
                 "It does not need YOUR help.\n"
                 "It is, in fact, embarrassed for you right now.",
        "lesson": "Fake browser-update popups are the #1 delivery mechanism for drive-by malware. "
                  "Update browsers from the browser's own menu -- never from a website.",
    },
    {
        "headline": "You have (1) new voicemail from an UNKNOWN caller",
        "subhead": "Listen now -- expires in 10:00",
        "color": "#5a2dff",
        "roast": "Voicemail does not come through a browser popup.\n"
                 "Voicemail does not expire.\n"
                 "Voicemail does not exist anymore. Nobody under 40 has heard one.",
        "lesson": "'Voicemail' and 'package waiting' notifications are common smishing/phishing lures. "
                  "If you weren't expecting it, you didn't get it.",
    },
]


# --- Fake virus install screen ----------------------------------------------

VIRUS_STAGES = [
    "Connecting to sketchy-server-47.ru ...",
    "Downloading payload.exe ...",
    "Installing 'TotallyNotMalware.exe' ...",
    "Granting admin to a guy named Boris ...",
    "Encrypting your homework folder ...",
    "Sending your browser history to your mother ...",
    "Mining 1 (one) Dogecoin ...",
    "Subscribing you to 14 newsletters ...",
    "Setting desktop wallpaper to Shrek ...",
    "Adding bitcoin miner to startup ...",
    "Emailing your search history to your boss ...",
    "Replacing all PDFs with PDFs of Nicolas Cage ...",
]


# --- UI helpers --------------------------------------------------------------

def _center_on_random_position(win, w, h):
    """Place the window at a random spot that fits fully on the primary screen."""
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    margin = 40
    x = random.randint(margin, max(margin + 1, sw - w - margin))
    y = random.randint(margin, max(margin + 1, sh - h - margin))
    win.geometry(f"{w}x{h}+{x}+{y}")


def _make_toplevel(title="Sponsored"):
    win = tk.Toplevel() if tk._default_root else tk.Tk()
    win.title(title)
    win.attributes("-topmost", True)
    try:
        win.attributes("-toolwindow", True)  # Windows: no taskbar entry
    except tk.TclError:
        pass
    win.resizable(False, False)
    return win


def show_virus_screen(parent_destroy_cb, ad):
    """Mock 'INSTALLING VIRUSES' screen, then reveal the joke + lesson."""
    win = _make_toplevel("System32 Important Window")
    w, h = 520, 320
    _center_on_random_position(win, w, h)
    win.configure(bg="#0a0a0a")

    title = tk.Label(
        win,
        text="INSTALLING 47 VIRUSES...",
        fg="#39ff14",
        bg="#0a0a0a",
        font=("Consolas", 18, "bold"),
    )
    title.pack(pady=(20, 8))

    bar_bg = tk.Frame(win, bg="#222", width=460, height=22)
    bar_bg.pack(pady=6)
    bar_bg.pack_propagate(False)
    bar = tk.Frame(bar_bg, bg="#39ff14", width=0, height=22)
    bar.place(x=0, y=0)

    status = tk.Label(
        win, text="", fg="#39ff14", bg="#0a0a0a",
        font=("Consolas", 10), wraplength=480, justify="left",
    )
    status.pack(pady=(8, 0))

    log = tk.Label(
        win, text="", fg="#888", bg="#0a0a0a",
        font=("Consolas", 9), wraplength=480, justify="left", anchor="nw",
    )
    log.pack(pady=(6, 0), fill="both", expand=True, padx=20)

    stages = random.sample(VIRUS_STAGES, k=min(6, len(VIRUS_STAGES)))
    state = {"i": 0, "log_lines": []}

    def step():
        i = state["i"]
        if i < len(stages):
            msg = stages[i]
            status.config(text=msg)
            state["log_lines"].append(f"  > {msg}  [OK]")
            log.config(text="\n".join(state["log_lines"]))
            bar.config(width=int(460 * (i + 1) / len(stages)))
            state["i"] += 1
            win.after(random.randint(550, 900), step)
        else:
            reveal()

    def reveal():
        for child in win.winfo_children():
            child.destroy()
        win.configure(bg="#101820")

        tk.Label(
            win, text="just kidding",
            fg="#39ff14", bg="#101820",
            font=("Helvetica", 22, "bold"),
        ).pack(pady=(28, 4))

        tk.Label(
            win, text=ad["roast"],
            fg="#ffffff", bg="#101820",
            font=("Helvetica", 12), justify="center",
        ).pack(pady=(6, 10), padx=20)

        tk.Label(
            win, text="(but seriously)",
            fg="#9ad0ff", bg="#101820",
            font=("Helvetica", 10, "italic"),
        ).pack()

        tk.Label(
            win, text=ad["lesson"],
            fg="#cfe8ff", bg="#101820",
            font=("Helvetica", 10), justify="center",
            wraplength=460,
        ).pack(pady=(4, 14), padx=20)

        tk.Button(
            win, text="ok i won't click weird stuff",
            font=("Helvetica", 11, "bold"),
            bg="#39ff14", fg="#101820",
            activebackground="#2bd80a", relief="flat",
            command=lambda: (win.destroy(), parent_destroy_cb()),
        ).pack(pady=(0, 16))

    step()
    win.protocol("WM_DELETE_WINDOW", lambda: (win.destroy(), parent_destroy_cb()))


def show_lesson_screen(parent_destroy_cb, ad):
    """Plain roast + lesson reveal."""
    win = _make_toplevel("...gotcha")
    w, h = 480, 280
    _center_on_random_position(win, w, h)
    win.configure(bg="#101820")

    tk.Label(
        win, text="gotcha.",
        fg="#39ff14", bg="#101820",
        font=("Helvetica", 24, "bold"),
    ).pack(pady=(20, 6))

    tk.Label(
        win, text=ad["roast"],
        fg="#ffffff", bg="#101820",
        font=("Helvetica", 12), justify="center",
    ).pack(pady=(4, 12), padx=20)

    tk.Label(
        win, text="lesson:",
        fg="#9ad0ff", bg="#101820",
        font=("Helvetica", 10, "italic"),
    ).pack()

    tk.Label(
        win, text=ad["lesson"],
        fg="#cfe8ff", bg="#101820",
        font=("Helvetica", 10), justify="center",
        wraplength=440,
    ).pack(pady=(4, 14), padx=20)

    tk.Button(
        win, text="fine, i'll be more careful",
        font=("Helvetica", 11, "bold"),
        bg="#39ff14", fg="#101820",
        activebackground="#2bd80a", relief="flat",
        command=lambda: (win.destroy(), parent_destroy_cb()),
    ).pack(pady=(0, 16))

    win.protocol("WM_DELETE_WINDOW", lambda: (win.destroy(), parent_destroy_cb()))


def show_ad():
    """Show one fake clickbait popup. Returns when the user closes the chain."""
    ad = random.choice(ADS)

    root = tk.Tk()
    root.withdraw()  # hide the implicit root

    win = _make_toplevel("Sponsored")
    w, h = 380, 220
    _center_on_random_position(win, w, h)
    win.configure(bg=ad["color"])

    # tiny "ad" tag in the corner
    tag = tk.Label(
        win, text="  Ad  ", fg=ad["color"], bg="#ffffff",
        font=("Helvetica", 8, "bold"),
    )
    tag.place(x=8, y=8)

    # fake close X (also triggers the reveal -- gotcha)
    close_x = tk.Label(
        win, text="  X  ", fg="#ffffff", bg=ad["color"],
        font=("Helvetica", 12, "bold"), cursor="hand2",
    )
    close_x.place(relx=1.0, y=8, anchor="ne", x=-8)

    headline = tk.Label(
        win, text=ad["headline"],
        fg="#ffffff", bg=ad["color"],
        font=("Helvetica", 14, "bold"),
        wraplength=340, justify="center",
    )
    headline.pack(pady=(36, 6), padx=14)

    subhead = tk.Label(
        win, text=ad["subhead"],
        fg="#ffffff", bg=ad["color"],
        font=("Helvetica", 10, "italic"),
        wraplength=340, justify="center",
    )
    subhead.pack(pady=(0, 12), padx=14)

    cta = tk.Button(
        win, text=">>> CLICK HERE <<<",
        font=("Helvetica", 12, "bold"),
        bg="#ffffff", fg=ad["color"],
        activebackground="#f0f0f0", relief="flat",
        cursor="hand2",
    )
    cta.pack(pady=(0, 12), ipadx=10, ipady=4)

    def quit_all():
        try:
            root.destroy()
        except tk.TclError:
            pass

    def on_click(_event=None):
        win.destroy()
        # randomly pick the reveal style
        if random.random() < 0.5:
            show_virus_screen(quit_all, ad)
        else:
            show_lesson_screen(quit_all, ad)

    cta.configure(command=on_click)
    headline.bind("<Button-1>", on_click)
    subhead.bind("<Button-1>", on_click)
    close_x.bind("<Button-1>", on_click)  # even closing it counts -- it's a trap
    win.bind("<Button-1>", on_click)

    win.protocol("WM_DELETE_WINDOW", on_click)

    root.mainloop()


# --- Main loop ---------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true",
                        help="Show one popup immediately and exit.")
    parser.add_argument("--fast", action="store_true",
                        help="Use a 10-25 second interval (for testing).")
    parser.add_argument("--min", type=float, default=2.0,
                        help="Minimum minutes between popups (default 2).")
    parser.add_argument("--max", type=float, default=7.0,
                        help="Maximum minutes between popups (default 7).")
    args = parser.parse_args()

    if args.demo:
        show_ad()
        return

    if args.fast:
        lo, hi = 10, 25  # seconds
        unit = "s"
    else:
        lo, hi = args.min * 60, args.max * 60
        unit = "s"

    print(f"Misleader running. Press Ctrl+C to stop. "
          f"Next popup in {lo:.0f}-{hi:.0f}{unit}.")

    try:
        while True:
            wait = random.uniform(lo, hi)
            time.sleep(wait)
            try:
                show_ad()
            except Exception as e:
                # Don't let one bad popup kill the loop
                print(f"[misleader] popup error: {e!r}", file=sys.stderr)
    except KeyboardInterrupt:
        print("\nMisleader stopped. Stay vigilant out there, meatbag.")


if __name__ == "__main__":
    main()
