#!/usr/bin/env python3

from gnuradio import gr, blocks, analog, audio, network, filter
from gnuradio.eng_arg import eng_float
from gnuradio.filter import firdes
import osmosdr
import argparse

class TopBlock(gr.top_block):
    def __init__(self, frequency, sample_rate, audio_rate, rf_gain, if_gain, tcp_port):
        gr.top_block.__init__(self, "Top Block")

        # Osmocom Source (supports HackRF)
        self.osmo_source = osmosdr.source()
        self.osmo_source.set_sample_rate(sample_rate)  # Set to 10M initially, will be decimated
        self.osmo_source.set_center_freq(frequency)
        self.osmo_source.set_gain(rf_gain)          # RF gain (LNA)
        self.osmo_source.set_if_gain(if_gain)       # IF gain (VGA)
        self.osmo_source.set_bb_gain(20)            # Baseband gain

        # First stage decimation to get closer to NFM bandwidth
        decimation1 = int(sample_rate / 1000000)  # Decimate to 1 MHz
        self.decim1 = filter.freq_xlating_fir_filter_ccc(
            decimation1,
            firdes.low_pass(1.0, sample_rate, 450000, 50000),
            0,
            sample_rate
        )

        # Second stage decimation to match SDR# NFM bandwidth (225 kHz)
        decimation2 = int(1000000 / 225000)
        self.decim2 = filter.freq_xlating_fir_filter_ccc(
            decimation2,
            firdes.low_pass(1.0, 1000000, 112500, 12500),
            0,
            1000000
        )

        # Final resampler to audio rate
        audio_decimation = int(225000 / audio_rate)
        self.resampler = filter.rational_resampler_ccf(
            interpolation=1,
            decimation=audio_decimation,
            taps=firdes.low_pass(1.0, 225000, 12500, 1500),
            fractional_bw=0.4
        )

        # Quadrature Demodulator (matching SDR# NFM settings)
        # SDR# uses 12.5 kHz deviation for NFM
        deviation = 12500
        quad_rate = audio_rate
        self.quad_demod = analog.quadrature_demod_cf(quad_rate/(2*3.14159*deviation))

        # DC Blocker
        self.dc_blocker = filter.dc_blocker_ff(32, True)

        # Audio Filter (matching SDR# NFM bandwidth)
        self.audio_filter = filter.fir_filter_fff(
            1,
            firdes.low_pass(
                1.0,
                audio_rate,
                5000,        # SDR# NFM audio cutoff
                1000,        # Transition width
            )
        )

        # Volume control
        self.volume = blocks.multiply_const_ff(1.0)  # Adjustable volume

        # Audio Sink
        self.audio_sink = audio.sink(audio_rate, "pulse", True)

        # TCP Sink
        self.tcp_sink = network.tcp_sink(
            itemsize=gr.sizeof_float,
            veclen=1,
            host="127.0.0.1",
            port=tcp_port,
            sinkmode=1,
        )

        # Connect the blocks
        self.connect(self.osmo_source, self.decim1)
        self.connect(self.decim1, self.decim2)
        self.connect(self.decim2, self.resampler)
        self.connect(self.resampler, self.quad_demod)
        self.connect(self.quad_demod, self.dc_blocker)
        self.connect(self.dc_blocker, self.audio_filter)
        self.connect(self.audio_filter, self.volume)
        self.connect(self.volume, self.tcp_sink)
        self.connect(self.volume, self.audio_sink)

def main():
    parser = argparse.ArgumentParser(description="FM Demodulation with HackRF")
    parser.add_argument("-f", "--frequency", type=float, required=True, help="Frequency in Hz (e.g., 155355000)")
    parser.add_argument("-s", "--sample-rate", type=float, default=10000000, help="Sample rate in Hz (default: 10 MSPS)")
    parser.add_argument("-a", "--audio-rate", type=int, default=48000, help="Audio sample rate in Hz (default: 48 kHz)")
    parser.add_argument("--rf-gain", type=float, default=16, help="RF gain in dB (default: 16 dB)")
    parser.add_argument("--if-gain", type=float, default=22, help="IF gain in dB (default: 22 dB)")
    parser.add_argument("-t", "--tcp-port", type=int, required=True, help="TCP port for streaming audio data")
    args = parser.parse_args()

    tb = TopBlock(args.frequency, args.sample_rate, args.audio_rate, args.rf_gain, args.if_gain, args.tcp_port)
    tb.start()
    tb.wait()

if __name__ == "__main__":
    main()