"""Tkinter GUI: pick an operation, load its input image(s), run it, preview the result.

Run with `gui` (console script) or `python -m gui.app`.
"""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk
from typing import Optional, cast

import imagelib
from describe_bmp import describe_image
from imagelib.image import Image, Size

from gui.preview import to_photo_image
from gui.registry import OPERATIONS, Operation, Param

PREVIEW_SIZE = 220
FILE_TYPES = [("Images", "*.bmp *.png"), ("Bitmap", "*.bmp"), ("PNG", "*.png"), ("All files", "*.*")]
SAMPLES_DIR = Path(__file__).resolve().parents[2] / "samples"

# Above this many pixels, warn before decoding: this project's BMP/PNG readers
# and every operation are pure-Python, per-pixel loops with no imaging-library
# acceleration, so a large image can take a long time.
LARGE_IMAGE_PIXELS = 2_000_000

# Stands in for a `Param`'s image-dependent default before any image is
# loaded (or if it's never loaded and the field is left untouched) - an
# 8-bit image, matching this project's classic default bit depth.
_DEFAULT_PARAM_IMAGE = Image("L", Size(1, 1))


def _resolve_param_default(param: Param, image: Optional[Image]) -> object:
	"""Resolve a `Param`'s pre-fill value, calling it with `image` if it's dynamic.

	Args:
		param: The parameter whose default to resolve.
		image: The operation's first input image, or None if it isn't
			loaded yet (in which case `_DEFAULT_PARAM_IMAGE` stands in).

	Returns:
		The value to pre-fill the parameter's entry field with.
	"""
	if not callable(param.default):
		return param.default
	return param.default(image if image is not None else _DEFAULT_PARAM_IMAGE)


class App(tk.Tk):
	"""The main application window: operation picker, inputs, params, and previews."""

	operation: Operation
	input_images: list[Optional[Image]]
	result_image: Optional[Image]
	param_vars: dict[str, tk.StringVar]
	_photo_refs: list[tk.PhotoImage]  # keep references alive, Tk drops GC'd images

	operation_combo: ttk.Combobox
	inputs_frame: ttk.Frame
	params_frame: ttk.Frame
	save_button: ttk.Button
	status_var: tk.StringVar

	input_preview_labels: list[ttk.Label]
	input_caption_vars: list[tk.StringVar]
	result_preview_label: ttk.Label
	result_caption_var: tk.StringVar

	def __init__(self) -> None:
		"""Build the window and select the first registered operation."""
		super().__init__()
		self.title("Operasi Citra Digital")

		self.operation: Operation = OPERATIONS[0]
		self.input_images: list[Optional[Image]] = []
		self.result_image: Optional[Image] = None
		self.param_vars: dict[str, tk.StringVar] = {}
		self._photo_refs: list[tk.PhotoImage] = []

		self._build_widgets()
		self._select_operation(OPERATIONS[0].key)

	# -- one-time layout ------------------------------------------------------

	def _build_widgets(self) -> None:
		"""Lay out the one-time widgets: operation picker, frames, and action buttons."""
		top = ttk.Frame(self, padding=8)
		top.pack(fill="x")
		ttk.Label(top, text="Operation:").pack(side="left")
		self.operation_combo = ttk.Combobox(
			top,
			state="readonly",
			width=55,
			values=[f"{op.category} - {op.label}" for op in OPERATIONS],
		)
		self.operation_combo.pack(side="left", padx=6)
		self.operation_combo.bind("<<ComboboxSelected>>", self._on_operation_selected)

		self.inputs_frame = ttk.Frame(self, padding=8)
		self.inputs_frame.pack(fill="x")

		self.params_frame = ttk.Frame(self, padding=8)
		self.params_frame.pack(fill="x")

		actions = ttk.Frame(self, padding=8)
		actions.pack(fill="x")
		ttk.Button(actions, text="Run", command=self._run).pack(side="left")
		self.save_button = ttk.Button(actions, text="Save result...", command=self._save_result, state="disabled")
		self.save_button.pack(side="left", padx=6)
		ttk.Button(actions, text="Describe image...", command=self._describe_image).pack(side="left", padx=6)

		self.status_var = tk.StringVar(value="Ready.")
		ttk.Label(self, textvariable=self.status_var, anchor="w", relief="sunken").pack(fill="x", side="bottom")

	# -- rebuilt whenever the selected operation changes -----------------------

	def _on_operation_selected(self, _event: object = None) -> None:
		"""Handle the operation combobox selection changing.

		Args:
			_event: The Tk selection event; unused, present to match the binding signature.
		"""
		index = self.operation_combo.current()
		self._select_operation(OPERATIONS[index].key)

	def _select_operation(self, key: str) -> None:
		"""Switch to the operation identified by `key` and rebuild dependent widgets.

		Args:
			key: The `Operation.key` of the operation to select.
		"""
		self.operation = next(op for op in OPERATIONS if op.key == key)
		self.operation_combo.current(OPERATIONS.index(self.operation))
		self.input_images = [None] * self.operation.num_inputs
		self.result_image = None
		self.save_button.config(state="disabled")
		self._rebuild_inputs()
		self._rebuild_params()
		self._refresh_previews()
		self.status_var.set(f"Selected: {self.operation.label}")

	def _rebuild_inputs(self) -> None:
		"""Rebuild the input-image slots (and their Load buttons) for the current operation."""
		for child in self.inputs_frame.winfo_children():
			child.destroy()
		self._photo_refs.clear()

		self.input_preview_labels: list[ttk.Label] = []
		self.input_caption_vars: list[tk.StringVar] = []
		for i in range(self.operation.num_inputs):
			slot = ttk.LabelFrame(self.inputs_frame, text=f"Image {chr(ord('A') + i)}")
			slot.pack(side="left", padx=6)
			preview = ttk.Label(slot, text="(none)", width=28, anchor="center")
			preview.pack(padx=4, pady=4)
			caption = tk.StringVar(value="")
			ttk.Label(slot, textvariable=caption).pack()
			buttons = ttk.Frame(slot)
			buttons.pack(pady=4)
			ttk.Button(buttons, text="Load...", command=lambda i=i: self._load_input(i)).pack(side="left")
			ttk.Button(
				buttons, text="Load from sample...", command=lambda i=i: self._load_sample_input(i)
			).pack(side="left", padx=(4, 0))
			self.input_preview_labels.append(preview)
			self.input_caption_vars.append(caption)

		result_slot = ttk.LabelFrame(self.inputs_frame, text="Result")
		result_slot.pack(side="left", padx=12)
		self.result_preview_label = ttk.Label(result_slot, text="(none)", width=28, anchor="center")
		self.result_preview_label.pack(padx=4, pady=4)
		self.result_caption_var = tk.StringVar(value="")
		ttk.Label(result_slot, textvariable=self.result_caption_var).pack()
		ttk.Label(result_slot, text=" ").pack(pady=4)  # keeps the row aligned with the input slots' button row

	def _rebuild_params(self) -> None:
		"""Rebuild the parameter entry fields for the current operation."""
		for child in self.params_frame.winfo_children():
			child.destroy()
		self.param_vars = {}
		first_image = self.input_images[0] if self.input_images else None
		for param in self.operation.params:
			row = ttk.Frame(self.params_frame)
			row.pack(fill="x", pady=2)
			ttk.Label(row, text=param.label, width=22, anchor="w").pack(side="left")
			var = tk.StringVar(value=str(_resolve_param_default(param, first_image)))
			if param.kind == "choice":
				widget: tk.Widget = ttk.Combobox(row, textvariable=var, state="readonly", values=list(param.choices))
			else:
				widget = ttk.Entry(row, textvariable=var)
			widget.pack(side="left", fill="x", expand=True)
			self.param_vars[param.name] = var

	# -- actions ----------------------------------------------------------------

	def _load_input(self, index: int) -> None:
		"""Prompt for a file and load it into input slot `index`.

		Args:
			index: The input slot to fill (0-based).
		"""
		self._pick_and_load_input(index, initialdir=None)

	def _load_sample_input(self, index: int) -> None:
		"""Prompt for a file under `samples/` and load it into input slot `index`.

		Args:
			index: The input slot to fill (0-based).
		"""
		self._pick_and_load_input(index, initialdir=str(SAMPLES_DIR))

	def _pick_and_load_input(self, index: int, initialdir: Optional[str]) -> None:
		"""Open a file picker and load the chosen image into input slot `index`.

		Args:
			index: The input slot to fill (0-based).
			initialdir: The directory the file dialog should open in, or None
				to use the dialog's default.
		"""
		if initialdir:
			path = filedialog.askopenfilename(title="Open image", filetypes=FILE_TYPES, initialdir=initialdir)
		else:
			path = filedialog.askopenfilename(title="Open image", filetypes=FILE_TYPES)
		if not path:
			return
		if not self._confirm_large_image(path):
			return
		try:
			image = imagelib.open(path)
		except Exception as exc:
			messagebox.showerror("Failed to open image", str(exc))
			return
		self.input_images[index] = image
		self.input_caption_vars[index].set(
			f"{Path(path).name}\n{image.width}x{image.height}, {image.mode} ({image.bits_per_pixel}-bit)"
		)
		self._set_preview(self.input_preview_labels[index], image)
		self.status_var.set(f"Loaded {Path(path).name} into Image {chr(ord('A') + index)}")
		if index == 0:
			self._refresh_dynamic_param_defaults()

	def _refresh_dynamic_param_defaults(self) -> None:
		"""Re-fill every image-dependent parameter field from the freshly (re)loaded Image A.

		Only fields whose `Param.default` is a callable are touched; any
		value the user already typed into a fixed-default field is left alone.
		"""
		first_image = self.input_images[0] if self.input_images else None
		if first_image is None:
			return
		for param in self.operation.params:
			if callable(param.default) and param.name in self.param_vars:
				self.param_vars[param.name].set(str(param.default(first_image)))

	def _collect_params(self) -> dict[str, object]:
		"""Read and convert the current operation's parameter entry fields.

		Returns:
			A dict mapping each `Param.name` to its converted value (int, float, or str).

		Raises:
			ValueError: If an `"int"` or `"float"` field's text can't be converted.
		"""
		values: dict[str, object] = {}
		for param in self.operation.params:
			raw = self.param_vars[param.name].get()
			if param.kind == "int":
				values[param.name] = int(raw)
			elif param.kind == "float":
				values[param.name] = float(raw)
			else:
				values[param.name] = raw
		return values

	def _run(self) -> None:
		"""Run the current operation on its loaded inputs and preview the result."""
		if any(image is None for image in self.input_images):
			messagebox.showwarning("Missing input", "Load all required input image(s) first.")
			return
		images = cast(list[Image], self.input_images)  # narrowed: the check above ruled out None

		if self.operation.describe_size_mismatch is not None and len(images) == 2:
			message = self.operation.describe_size_mismatch(*images)
			if message is not None:
				messagebox.showwarning("Different image sizes", message)
		try:
			params = self._collect_params()
		except ValueError as exc:
			messagebox.showerror("Invalid parameter", f"Check the operation's parameters: {exc}")
			return
		try:
			self.result_image = self.operation.run(*images, **params)
		except Exception as exc:
			messagebox.showerror("Operation failed", str(exc))
			return

		self._set_preview(self.result_preview_label, self.result_image)
		self.result_caption_var.set(
			f"{self.result_image.width}x{self.result_image.height}, "
			f"{self.result_image.mode} ({self.result_image.bits_per_pixel}-bit)"
		)
		self.status_var.set(f"Ran: {self.operation.label}")
		self.save_button.config(state="normal")

	def _save_result(self) -> None:
		"""Prompt for a destination path and save the last run result to it."""
		if self.result_image is None:
			return
		path = filedialog.asksaveasfilename(
			title="Save result",
			defaultextension=".png",
			filetypes=[("PNG", "*.png"), ("Bitmap", "*.bmp")],
		)
		if not path:
			return
		try:
			self.result_image.save(path)
		except Exception as exc:
			messagebox.showerror("Failed to save image", str(exc))
			return
		self.status_var.set(f"Saved {path}")

	def _describe_image(self) -> None:
		"""Open an image and show its color depth, resolution, and pixel values."""
		path = filedialog.askopenfilename(title="Open image to describe", filetypes=FILE_TYPES)
		if not path:
			return
		if not self._confirm_large_image(path):
			return
		try:
			image = imagelib.open(path)
		except Exception as exc:
			messagebox.showerror("Failed to open image", str(exc))
			return
		report = f"File: {path}\n{describe_image(image)}"
		self._show_report(f"Describe: {Path(path).name}", report)

	def _confirm_large_image(self, path: str) -> bool:
		"""Warn and ask for confirmation before decoding `path` if it's large.

		Peeks at the file's dimensions (cheap: header-only, no pixel decode)
		and, if it's above `LARGE_IMAGE_PIXELS`, asks the user to confirm
		before proceeding, since decoding and processing it will be slow.

		Args:
			path: Path to the image file about to be opened.

		Returns:
			True if loading should proceed, False if the user backed out.
		"""
		try:
			width, height = imagelib.peek_size(path)
		except Exception:
			return True  # let imagelib.open raise the real error
		pixels = width * height
		if pixels <= LARGE_IMAGE_PIXELS:
			return True
		megapixels = pixels / 1_000_000
		return messagebox.askyesno(
			"Large image",
			f"{Path(path).name} is {width}x{height} ({megapixels:.1f} MP).\n\n"
			"This app decodes and processes images pixel-by-pixel in pure "
			"Python (no imaging libraries), so this may take a while. Continue?",
		)

	def _show_report(self, title: str, text: str) -> None:
		"""Show `text` in a scrollable, read-only popup window.

		Args:
			title: The popup window's title.
			text: The (read-only) text to display.
		"""
		window = tk.Toplevel(self)
		window.title(title)
		window.geometry("480x480")
		widget = scrolledtext.ScrolledText(window, wrap="none")
		widget.insert("1.0", text)
		widget.configure(state="disabled")
		widget.pack(fill="both", expand=True)

	# -- previews ---------------------------------------------------------------

	def _refresh_previews(self) -> None:
		"""Refresh every input preview and the result preview from current state."""
		for i, label in enumerate(self.input_preview_labels):
			self._set_preview(label, self.input_images[i])
		self._set_preview(self.result_preview_label, self.result_image)

	def _set_preview(self, label: ttk.Label, image: Optional[Image]) -> None:
		"""Render `image` into a preview label, or clear it if `image` is None.

		Args:
			label: The preview label widget to update.
			image: The image to preview, or None to show a placeholder.
		"""
		if image is None:
			label.configure(image="", text="(none)")
			return
		photo = to_photo_image(image, max_size=PREVIEW_SIZE)
		self._photo_refs.append(photo)  # Tk only keeps a weak reference internally
		label.configure(image=photo, text="")


def main() -> None:
	"""Launch the GUI and block until the window is closed."""
	App().mainloop()


if __name__ == "__main__":
	main()
