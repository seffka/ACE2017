clear

% set path to audio degradation tool box.
addpath(genpath(fullfile(pwd,'../audio-degradation-toolbox/AudioDegradationToolbox')));
% input
srcAudio='~/Desktop/MIR/Beatles/audio'
% output
dstAudio='~/Desktop/MIR/Beatles/vinyl'
listing = dir(srcAudio);
pathnames=string.empty;
filenames=string.empty;
for i = 1:size(listing)
    if (~listing(i).isdir)
        pathnames(end + 1) = strcat(listing(i).folder, '/', listing(i).name);
        filenames(end+1)=listing(i).name
    end    
end   
if ~exist(dstAudio,'dir'), mkdir(dstAudio); end

createSpectrograms = 0;

%%
% just copying original files to the demo folder
%maxValueRangeVis = zeros(length(pathnames));
%for k=1:length(pathnames)
%    copyfile(pathnames{k}, fullfile(pathOutputDemo,sprintf('00_Original_file%d.wav',k)))
%    if createSpectrograms
%        [f_audio,samplingFreq]=audioread(pathnames{k});
%        [s,f,t] = spectrogram(f_audio,hamming(round(samplingFreq*0.093)),round(samplingFreq*0.093/2),[],samplingFreq);
%        figure; imagesc(t,f,log10(abs(s)+1)); axis xy; colormap(hot); ylim([0,8000]); colorbar; print('-dpng', fullfile(pathOutputDemo,sprintf('00_Original_file%d.png',k)))
%        maxValueRangeVis(k) = max(max(log10(abs(s)+1)));
%    end
%end

%%
for k=1:length(pathnames)
    [f_audio,samplingFreq]=audioread(char(pathnames(k)));
    f_audio_out = applyDegradation('vinylRecording', f_audio, samplingFreq);
    audiowrite(fullfile(dstAudio, char(filenames(k))), f_audio_out,samplingFreq, 'BitsPerSample', 16);
    if createSpectrograms
        [s,f,t] = spectrogram(f_audio_out,hamming(round(samplingFreq*0.093)),round(samplingFreq*0.093/2),[],samplingFreq);
        figure; imagesc(t,f,log10(abs(s)+1),[0 maxValueRangeVis(k)]); axis xy; colormap(hot); ylim([0,8000]); colorbar; print('-dpng', fullfile(pathOutputDemo,sprintf('Degr_01_liveRecording_file%d.png',k)))
    end
end



