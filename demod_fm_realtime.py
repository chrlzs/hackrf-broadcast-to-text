#!/usr/bin/env python3

from gnuradio import gr, blocks, analog, audio, network, filter
from gnuradio.eng_arg import eng_float
from gnuradio.filter import firdes
import osmosdr
import argparse

class TopBlock(gr.top_block):
    def __init__(self, frequency, sample_rate, tcp_port, udp_port=None):
        gr.top_block.__init__(self, "Top Block")

        # Osmocom Source (supports HackRF)
        self.osmo_source = osmosdr.source()
        self.osmo_source.set_sample_rate(sample_rate)
        self.osmo_source.set_center_freq(frequency)
        self.osmo_source.set_gain(40)
        self.osmo_source.set_if_gain(40)
        self.osmo_source.set_bb_gain(40)

        # Rational Resampler (adjust sample rate if needed)
        self.resampler = filter.rational_resampler_ccf(
            interpolation=48,
            decimation=200,
            taps=[],
            fractional_bw=0.4,
        )

        # Quadrature Demodulator (FM demodulation)
        self.quad_demod = analog.quadrature_demod_cf(1.0)

        # Audio Sink (optional, for debugging)
        self.audio_sink = audio.sink(48000, "pulse", True)

        # TCP Sink (stream audio data to Python script)
        self.tcp_sink = network.tcp_sink(
            itemsize=gr.sizeof_float,  # Size of each item (float)
            veclen=1,                 # Vector length (1 for scalar)
            host="127.0.0.1",         # Host IP address
            port=tcp_port,            # TCP port
            sinkmode=1,               # Server mode (1 for server)
        )

        # UDP Sink (alternative to TCP)
        if udp_port:
            self.udp_sink = network.udp_sink(
                itemsize=gr.sizeof_float,
                host="127.0.0.1",
                port=udp_port,
                payload_size=1472,
                eof=True,
            )

        # Connect the blocks
        self.connect(self.osmo_source, self.resampler, self.quad_demod)
        self.connect(self.quad_demod, self.tcp_sink)
        if udp_port:
            self.connect(self.quad_demod, self.udp_sink)
        self.connect(self.quad_demod, self.audio_sink)  # Optional, for debugging

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="FM Demodulation with HackRF")
    parser.add_argument("-f", "--frequency", type=float, required=True, help="Frequency in Hz (e.g., 155355000)")
    parser.add_argument("-s", "--sample-rate", type=float, default=1000000, help="Sample rate in Hz (default: 1 MS/s)")
    parser.add_argument("-t", "--tcp-port", type=int, required=True, help="TCP port for streaming audio data")
    parser.add_argument("-u", "--udp-port", type=int, help="UDP port for streaming audio data")
    args = parser.parse_args()

    # Create and run the flowgraph
    tb = TopBlock(args.frequency, args.sample_rate, args.tcp_port, args.udp_port)
    tb.start()
    tb.wait()

if __name__ == "__main__":
    main()