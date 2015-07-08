function [ delta, theta, alpha, beta, gamma ] = Bandify( segment )
%Bandify Perform FFT on a segment of data to produce EEG spectral band information

x = segment;
m = length(x);
n = pow2(nextpow2(m));

y = fft(x,n);
power = y.*conj(y)/n;

% all bands are +1 freq because the first index is 0 for freq
deltas = log( power(2:4) );
thetas = log( power(5:8) );
alphas = log( power(9:14) );
betas = log( power(15:31 ) );
gammas = log( power( 32:43 ) );

delta = sum( deltas );
theta = sum( thetas );
alpha = sum( alphas );
beta = sum( betas );
gamma = sum( gammas );

end