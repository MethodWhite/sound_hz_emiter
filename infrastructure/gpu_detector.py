import subprocess

class GPUDetector:
    @staticmethod
    def select_gpu_backend():
        try:
            # Intentar usar OpenCL como primera opción
            import pyopencl
            return "opencl"
        except ImportError:
            return "cpu"