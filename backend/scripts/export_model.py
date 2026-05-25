"""
Model Export Script.
Exports trained PyTorch model to ONNX or TorchScript for deployment.
"""

import argparse
import os

import numpy as np
import torch

from backend.config import CHECKPOINTS_DIR, IMAGE_SIZE
from backend.models.cnn_model import CNNDetector
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def export_to_onnx(
    model: torch.nn.Module,
    output_path: str,
    input_size: tuple = (1, 3, *IMAGE_SIZE),
) -> None:
    """
    Export *model* to ONNX format.
    """
    model.eval()
    dummy = torch.randn(*input_size)

    torch.onnx.export(
        model,
        dummy,
        output_path,
        input_names=["input"],
        output_names=["output"],
        dynamic_axes={
            "input": {0: "batch_size"},
            "output": {0: "batch_size"},
        },
        opset_version=17,
    )
    logger.info("ONNX model exported to %s", output_path)

    # Quick verification
    import onnx
    onnx_model = onnx.load(output_path)
    onnx.checker.check_model(onnx_model)
    logger.info("ONNX model verified successfully")


def export_to_torchscript(
    model: torch.nn.Module,
    output_path: str,
    method: str = "trace",
    input_size: tuple = (1, 3, *IMAGE_SIZE),
) -> None:
    """
    Export *model* to TorchScript (for C++ / mobile deployment).

    Parameters
    ----------
    method : str
        ``"trace"`` for ``torch.jit.trace`` (no control flow),
        ``"script"`` for ``torch.jit.script`` (with control flow).
    """
    model.eval()

    if method == "trace":
        dummy = torch.randn(*input_size)
        scripted = torch.jit.trace(model, dummy)
    elif method == "script":
        scripted = torch.jit.script(model)
    else:
        raise ValueError(f"Unknown method: {method!r}")

    scripted.save(output_path)
    logger.info("TorchScript model exported to %s  (method=%s)", output_path, method)


def verify_export(
    original_model: torch.nn.Module,
    exported_path: str,
    input_size: tuple = (1, 3, *IMAGE_SIZE),
) -> bool:
    """
    Verify that the exported model produces the same outputs as the original.
    """
    original_model.eval()
    dummy = torch.randn(*input_size)

    with torch.no_grad():
        orig_out = original_model(dummy).numpy()

    if exported_path.endswith(".onnx"):
        import onnxruntime as ort
        session = ort.InferenceSession(exported_path)
        export_out = session.run(None, {"input": dummy.numpy()})[0]
    else:
        loaded = torch.jit.load(exported_path)
        with torch.no_grad():
            export_out = loaded(dummy).numpy()

    max_diff = float(np.max(np.abs(orig_out - export_out)))
    ok = max_diff < 1e-4
    logger.info(
        "Export verification: max_diff=%.6e  %s",
        max_diff, "PASSED" if ok else "FAILED",
    )
    return ok


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export the Deepfake Detector model")
    parser.add_argument(
        "--checkpoint", type=str,
        default=os.path.join(CHECKPOINTS_DIR, "best.pth"),
    )
    parser.add_argument(
        "--format", choices=["onnx", "torchscript"], default="onnx",
    )
    parser.add_argument("--output", type=str, default="model_export")
    parser.add_argument(
        "--method", type=str, default="trace",
        help="TorchScript method: trace or script",
    )
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()

    model = CNNDetector()
    if os.path.isfile(args.checkpoint):
        model.load_weights(args.checkpoint)

    if args.format == "onnx":
        path = f"{args.output}.onnx"
        export_to_onnx(model, path)
    else:
        path = f"{args.output}.pt"
        export_to_torchscript(model, path, method=args.method)

    if args.verify:
        verify_export(model, path)
