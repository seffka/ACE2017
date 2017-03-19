listing = dir('/Users/seffka/Desktop/MIR/Beatles/audio/*.wav');
outDir = '/Users/seffka/Desktop/MIR/Beatles/ChromaFeatures/chromas'
for i=1:length(listing)
    parts = strsplit(listing(i).name, '.');
    parts{end} = 'clp';
    clpFileName = strjoin(parts, '.');
    parts{end} = 'crp';
    crpFileName = strjoin(parts, '.');
    [f_audio,sideinfo]=wav_to_audio(listing(i).folder,'/',listing(i).name);

    shiftFB=estimateTuning(f_audio);
    paramPitch.winLenSTMSP=2048;
    paramPitch.shiftFB=shiftFB;
    paramPitch.visualize=0;
    [f_pitch,sideinfo]=...
        audio_to_pitch_via_FB(f_audio,paramPitch,sideinfo);
    
    paramCLP.applyLogCompr=1;
    paramCLP.factorLogCompr=100;
    paramCLP.visualize=0;
    paramCLP.save = 0;
    paramCLP.inputFeatureRate=sideinfo.pitch.featureRate;
    [f_CLP,sideinfo]=pitch_to_chroma(f_pitch,paramCLP,sideinfo);
    dlmwrite(strcat(outDir, '/', clpFileName), f_CLP', '\t');
    
    paramCRP.coeffsToKeep=[55:120];
    paramCRP.visualize=0;
    paramCRP.inputFeatureRate=sideinfo.pitch.featureRate;
    [f_CRP,sideinfo]=pitch_to_CRP(f_pitch,paramCRP,sideinfo);
    dlmwrite(strcat(outDir, '/', crpFileName), f_CRP', '\t');
end
