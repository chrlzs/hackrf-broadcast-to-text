#!/usr/bin/env python3

import numpy as np
from gnuradio import gr, blocks, analog
import os

class TopBlock(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self, "Top Block")

        # File source (raw IQ data)
        self.file_source = blocks.file_source(gr.sizeof_gr_complex, "fire_dispatch.raw", False)

        # Quadrature demodulator (FM demodulation)
        self.quad_demod = analog.quadrature_demod_cf(1.0)

        # Audio sink (save to WAV file)
        self.audio_sink = blocks.wavfile_sink(
            filename="fire_dispatch.wav",
            n_channels=1,
            sample_rate=48000,
            format=blocks.FORMAT_WAV,
            subformat=blocks.FORMAT_PCM_16,
            append=False
        )

        # Connect the blocks
        self.connect(self.file_source, self.quad_demod, self.audio_sink)

def main():
    tb = TopBlock()
    tb.start()
    tb.wait()

if __name__ == "__main__":
    main()