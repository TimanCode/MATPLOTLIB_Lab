import tkinter as tk

from window import GraphApp


def main() -> None:
    root = tk.Tk()
    GraphApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
