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
        self.osmo_source.set_sample_rate(sample_rate)
        self.osmo_source.set_center_freq(frequency)
        self.osmo_source.set_gain(rf_gain)          # RF gain (LNA)
        self.osmo_source.set_if_gain(if_gain)       # IF gain (VGA)
        self.osmo_source.set_bb_gain(20)            # Increased BB gain for better signal

        # Add AGC block for better signal levels
        self.agc = analog.agc_cc(1e-3, 1.0, 1.0)
        self.agc.set_max_gain(65536)

        # Rational Resampler (adjusted for better audio quality)
        self.resampler = filter.rational_resampler_ccf(
            interpolation=1,
            decimation=int(sample_rate / 48000),  # Dynamic decimation based on sample rate
            taps=firdes.low_pass(1.0, sample_rate, 12500, 1500),
            fractional_bw=0.4,
        )

        # Quadrature Demodulator (adjusted for NFM)
        quad_demod_gain = 0.225  # Adjusted for narrow-band FM
        self.quad_demod = analog.quadrature_demod_cf(quad_demod_gain)

        # DC Blocker (improved parameters)
        self.dc_blocker = filter.dc_blocker_ff(64, True)  # Increased length for better DC removal

        # Band-Pass Filter (adjusted for voice frequencies)
        self.band_pass_filter = filter.fir_filter_fff(
            1,
            firdes.band_pass(
                2.0,               # Increased gain
                audio_rate,        
                250,              # Slightly lower low cutoff
                3500,             # Slightly higher high cutoff
                400               # Narrower transition
            )
        )

        # Low-Pass Filter (adjusted for NFM bandwidth)
        self.low_pass_filter = filter.fir_filter_fff(
            1,
            firdes.low_pass(
                2.0,               # Increased gain
                audio_rate,
                5000,             # Adjusted cutoff for NFM
                1500              # Narrower transition
            )
        )

        # Add squelch block
        self.squelch = analog.pwr_squelch_ff(
            -50,           # Threshold in dB
            0.01,         # Alpha (attack/decay)
            0,            # Ramp
            True          # Gate
        )

        # Volume control (multiply constant)
        self.volume = blocks.multiply_const_ff(1.5)  # Boost volume slightly

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

        # Connect the blocks with new AGC and squelch
        self.connect(self.osmo_source, self.agc)
        self.connect(self.agc, self.resampler)
        self.connect(self.resampler, self.quad_demod)
        self.connect(self.quad_demod, self.dc_blocker)
        self.connect(self.dc_blocker, self.band_pass_filter)
        self.connect(self.band_pass_filter, self.low_pass_filter)
        self.connect(self.low_pass_filter, self.squelch)
        self.connect(self.squelch, self.volume)
        self.connect(self.volume, self.tcp_sink)
        self.connect(self.volume, self.audio_sink)

def main():
    parser = argparse.ArgumentParser(description="FM Demodulation with HackRF")
    parser.add_argument("-f", "--frequency", type=float, required=True, help="Frequency in Hz (e.g., 155355000)")
    parser.add_argument("-s", "--sample-rate", type=float, default=225000, help="Sample rate in Hz (default: 225 kHz)")
    parser.add_argument("-a", "--audio-rate", type=int, default=48000, help="Audio sample rate in Hz (default: 48 kHz)")
    parser.add_argument("--rf-gain", type=float, default=16, help="RF gain in dB (default: 16 dB)")  # Matched to your SDR# settings
    parser.add_argument("--if-gain", type=float, default=22, help="IF gain in dB (default: 22 dB)")  # Matched to your SDR# settings
    parser.add_argument("-t", "--tcp-port", type=int, required=True, help="TCP port for streaming audio data")
    args = parser.parse_args()

    tb = TopBlock(args.frequency, args.sample_rate, args.audio_rate, args.rf_gain, args.if_gain, args.tcp_port)
    tb.start()
    tb.wait()

if __name__ == "__main__":
    main()