#!/usr/bin/env python3

from gnuradio import gr, blocks, analog, audio, network, filter, qtgui
from gnuradio.eng_arg import eng_float
from gnuradio.filter import firdes
import osmosdr
import argparse

class TopBlock(gr.top_block):
    def __init__(self, frequency, sample_rate, audio_rate, rf_gain, if_gain, tcp_port):
        gr.top_block.__init__(self, "Top Block")

        # Osmocom Source (supports HackRF)
        self.osmo_source = osmosdr.source()
        self.osmo_source.set_sample_rate(sample_rate)
        self.osmo_source.set_center_freq(frequency)
        self.osmo_source.set_gain(rf_gain)          # RF gain (LNA)
        self.osmo_source.set_if_gain(if_gain)       # IF gain (VGA)
        self.osmo_source.set_bb_gain(0)             # BB gain (set to 0)

        # Rational Resampler (adjust sample rate if needed)
        self.resampler = filter.rational_resampler_ccf(
            interpolation=1,
            decimation=5,  # Adjusted decimation
            taps=[],
            fractional_bw=0.4,
        )

        # Quadrature Demodulator (FM demodulation)
        self.quad_demod = analog.quadrature_demod_cf(0.20)  # Adjusted gain

        # DC Blocker (remove DC offset)
        self.dc_blocker = filter.dc_blocker_ff(32, True)

        # Low-Pass Filter (clean up audio)
        self.low_pass_filter = filter.fir_filter_fff(
            1,  # Decimation factor (1 for no decimation)
            firdes.low_pass(1.0, audio_rate, 12500, 2500)  # Default window
        )

        # Audio Sink (optional, for debugging)
        self.audio_sink = audio.sink(audio_rate, "pulse", True)

        # TCP Sink (stream audio data to Python script)
        self.tcp_sink = network.tcp_sink(
            itemsize=gr.sizeof_float,  # Size of each item (float)
            veclen=1,                 # Vector length (1 for scalar)
            host="127.0.0.1",         # Host IP address
            port=tcp_port,            # TCP port
            sinkmode=1,               # Server mode (1 for server)
        )

        # Connect the blocks
        self.connect(self.osmo_source, self.resampler, self.quad_demod)
        self.connect(self.quad_demod, self.dc_blocker)
        self.connect(self.dc_blocker, self.low_pass_filter)
        self.connect(self.low_pass_filter, self.tcp_sink)
        self.connect(self.low_pass_filter, self.audio_sink)  # Optional, for debugging

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="FM Demodulation with HackRF")
    parser.add_argument("-f", "--frequency", type=float, required=True, help="Frequency in Hz (e.g., 155355000)")
    parser.add_argument("-s", "--sample-rate", type=float, default=225000, help="Sample rate in Hz (default: 225 kHz)")
    parser.add_argument("-a", "--audio-rate", type=int, default=48000, help="Audio sample rate in Hz (default: 48 kHz)")
    parser.add_argument("--rf-gain", type=float, default=16, help="RF gain in dB (default: 16 dB)")
    parser.add_argument("--if-gain", type=float, default=22, help="IF gain in dB (default: 22 dB)")
    parser.add_argument("-t", "--tcp-port", type=int, required=True, help="TCP port for streaming audio data")
    args = parser.parse_args()

    # Create and run the flowgraph
    tb = TopBlock(args.frequency, args.sample_rate, args.audio_rate, args.rf_gain, args.if_gain, args.tcp_port)
    tb.start()
    tb.wait()

if __name__ == "__main__":
    main()