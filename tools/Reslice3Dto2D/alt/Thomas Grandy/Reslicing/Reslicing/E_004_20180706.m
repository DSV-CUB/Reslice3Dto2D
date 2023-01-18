%% ID 004 reslicing and preparing for manual segmentation

%% define id
id  = '004';

%% raw data path
fn0 = ['C:\THG_Data\3DCS_original\' id '\'];

%% output data files/paths
fn1 = ['C:\THG\3DCS_LV_1\B_data\A_DicomInfo\DicomInfo_' id '.mat'];
pna = ['C:\THG\3DCS_LV_1\B_data\E_CVI\3DCS_' id '_LGE'];
pnb = ['C:\THG\3DCS_LV_1\B_data\E_CVI\3DCS_' id '_CS'];

%% load data analysis randomization
load(strcat(pwd, '\rand_data_analysis_LV_1.mat'));

%% add paths
addpath(strcat(pwd, '\Functions\'));
addpath(strcat(pwd, '\Tools\DicomToolbox'));

%% read & save headers if not existent
load(fn1,'DicomInfo')

%% define file #
cs   = 67;
lge  = [44:2:58];
lax  = [38 42 40];
cine = [8 9 10 24:35];

%% find indices cs
for j = 1:length(DicomInfo)
    if isfield(DicomInfo(j).DicomInfo,'SeriesNumber')
    if DicomInfo(j).DicomInfo.SeriesNumber == cs
        cs_ = j;
    end
    end
end

%% find indices lge
for i = 1:length(lge)
    for j = 2:length(DicomInfo)
        if isfield(DicomInfo(j).DicomInfo,'SeriesNumber')
        if DicomInfo(j).DicomInfo.SeriesNumber == lge(i)
            lge_(i) = j;
        end
        end
    end
end
clearvars i j

%% find indices lax
for i = 1:length(lax)
    for j = 1:length(DicomInfo)
        if isfield(DicomInfo(j).DicomInfo,'SeriesNumber')
        if DicomInfo(j).DicomInfo.SeriesNumber == lax(i)
            lax_(i) = j;
        end
        end
    end
end

%% find indices cine
for i = 1:length(cine)
    for j = 1:length(DicomInfo)
        if isfield(DicomInfo(j).DicomInfo,'SeriesNumber')
        if DicomInfo(j).DicomInfo.SeriesNumber == cine(i)
            cine_(i) = j;
        end
        end
    end
end


%% SAX 

%% load 3D CS data
CS = zeros(DicomInfo(1,cs_).Sizes);
for j = 1:length(DicomInfo(1,cs_).Filenames)    
    CS(:,:,j) = dicomread(DicomInfo(1,cs_).Filenames{j,1});   
end; clearvars j
CS_info = DicomInfo(1,cs_);

%% get 3D CS coordinates
[X,Y,Z] = get_volume_coordinates_THG_20180510(CS,CS_info);

%% load sax slices, reslice and save as .dcm
for k = 1:length(lge_)
    
    % load slice
    LGE         = double(dicomread(DicomInfo(1,lge_(k)).Filenames{1,1}));
    LGE_info    = DicomInfo(1,lge_(k));
    
    % reslice 1: get coordinates
    % coordinates = get_slice_coordinates_THG_20180510(LGE,LGE_info);
    coordinates = get_slice_coordinates_and_change_resolution_THG_20180525(LGE,LGE_info,0.5); % increase resolution by factor 2    
    
    % reslice 2: reslice (using linear interpolation)
    tmp     = slice(X,Y,Z,CS,squeeze(coordinates(:,:,1)),squeeze(coordinates(:,:,2)),squeeze(coordinates(:,:,3)));
    tmp_slc = get(tmp,'CData');
    CS_slc  = permute(tmp_slc,[2 1]);
    close all
    
    % plot for checking
    %  figure;
    %  subplot(121); hold on; imagesc(LGE); colormap gray; title('Standard LGE')
    %  subplot(122); hold on; imagesc(CS_slc); colormap gray; title('CS')
    
    % change DicomInfo for saving
    info = LGE_info.DicomInfo;
       
    info.FileModDate = [];
    info.InstanceCreationDate = [];
    info.StudyDate = '19710101';
    info.SeriesDate = '19710101';
    info.AcquisitionDate = '19710101';
    info.ContentDate = '19710101';
    
    info.PatientsBirthDate = info.PatientBirthDate;
    info.PatientsSex = info.PatientSex;
    info.StudyDescription = '3DCS';
    info.PatientName.FamilyName = ['3DCS_rand_' num2str(randomization{1,3})];
    
    info.Width  = size(CS_slc,2);
    info.Height = size(CS_slc,1);
    
    info.PixelSpacing = info.PixelSpacing / 2;
    
    % save CS data
    dicomwrite(uint16(CS_slc),[pnb '\SAX_Series_' num2str(lge(k)) '.dcm'],info,'IOD','MR Image Storage');
    
    % clear variables
    clearvars LGE LGE_info coordinates tmp* CS_slc info
    
end; clearvars k

% clear variables
clearvars CS LGE CS_ LGE_ DicomInfo_ CS_info X Y Z

%% LAX

%% load 3D CS data
CS = zeros(DicomInfo(1,cs_).Sizes);
for j = 1:length(DicomInfo(1,cs_).Filenames)    
    CS(:,:,j) = dicomread(DicomInfo(1,cs_).Filenames{j,1});   
end; clearvars j
CS_info = DicomInfo(1,cs_);

%% get 3D CS coordinates
[X,Y,Z] = get_volume_coordinates_THG_20180510(CS,CS_info);

%% load lax slices, reslice, interpolate, & save as .dcm
for k = 1:length(lax_)
    
    % load slice
    LGE         = double(dicomread(DicomInfo(1,lax_(k)).Filenames{1,1}));
    LGE_info    = DicomInfo(1,lax_(k));
    
    % reslice 1: get coordinates
    % coordinates = get_slice_coordinates_THG_20180510(LGE,LGE_info);
    coordinates = get_slice_coordinates_and_change_resolution_THG_20180525(LGE,LGE_info,0.5); % increase resolution by factor 2    
    
    % reslice 2: reslice (using linear interpolation)
    tmp     = slice(X,Y,Z,CS,squeeze(coordinates(:,:,1)),squeeze(coordinates(:,:,2)),squeeze(coordinates(:,:,3)));
    tmp_slc = get(tmp,'CData');
    CS_slc  = permute(tmp_slc,[2 1]);
    close all
    
    % plot for checking
    % figure;
    % subplot(121); hold on; imagesc(LGE); colormap gray; title('Standard LGE')
    % subplot(122); hold on; imagesc(CS_slc); colormap gray; title('CS')
    
        
    % change DicomInfo for saving
    info = LGE_info.DicomInfo;
       
    info.FileModDate = [];
    info.InstanceCreationDate = [];
    info.StudyDate = '19710101';
    info.SeriesDate = '19710101';
    info.AcquisitionDate = '19710101';
    info.ContentDate = '19710101';
    
    info.PatientsBirthDate = info.PatientBirthDate;
    info.PatientsSex = info.PatientSex;
    info.StudyDescription = '3DCS';
    info.PatientName.FamilyName = ['3DCS_rand_' num2str(randomization{1,3})];

    info.Width  = size(CS_slc,2);
    info.Height = size(CS_slc,1);
    
    info.PixelSpacing = info.PixelSpacing / 2;
    
    % save CS data
    dicomwrite(uint16(CS_slc),[pnb '\LAX_Series_' num2str(lge(k)) '.dcm'],info,'IOD','MR Image Storage');
    
    % clear variables
    clearvars LGE LGE_info coordinates tmp* CS_slc info
    
end; clearvars k

% clear variables
clearvars CS LGE CS_* LGE_* DicomInfo_* CS_info X Y Z

%% load, rename and save cines
for k = 1:length(cine_)
    
    fn = DicomInfo(cine_(k)).Filenames;
    
    for l = 1:length(fn)
        
        info = dicominfo(fn{l});
        data = dicomread(fn{l});

        % LGE - change DicomInfo for saving
        info.FileModDate = [];
        info.InstanceCreationDate = [];
        info.StudyDate = '19700101';
        info.SeriesDate = '19700101';
        info.AcquisitionDate = '19700101';
        info.ContentDate = '19700101';
        
        info.PatientsBirthDate = info.PatientBirthDate;
        info.PatientsSex = info.PatientSex;
        info.StudyDescription = '3DCS';
        info.PatientName.FamilyName = ['3DCS_rand_' num2str(randomization{1,2})];
             
        % LGE - save data
        dicomwrite(data,[pna '\' fn{l}(end-7:end) '.dcm'],info,'IOD','MR Image Storage');
        
        % CS - change DicomInfo for saving
        info.FileModDate = [];
        info.InstanceCreationDate = [];
        info.StudyDate = '19710101';
        info.SeriesDate = '19710101';
        info.AcquisitionDate = '19710101';
        info.ContentDate = '19710101';
        
        info.PatientName.FamilyName = ['3DCS_rand_' num2str(randomization{1,3})];
             
        % CS - save data
        dicomwrite(data,[pnb '\' fn{l}(end-7:end) '.dcm'],info,'IOD','MR Image Storage');

        % clear variables
        clearvars info data
        
    end; clear l
    
    % clear variables
    clearvars fn
    
end; clear k

%% load, rename and save lge sax
for k = 1:length(lge_)
    
    fn = DicomInfo(lge_(k)).Filenames;
    
    for l = 1:length(fn)
        
        info = dicominfo(fn{l});
        data = dicomread(fn{l});

        % LGE - change DicomInfo for saving
        info.FileModDate = [];
        info.InstanceCreationDate = [];
        info.StudyDate = '19700101';
        info.SeriesDate = '19700101';
        info.AcquisitionDate = '19700101';
        info.ContentDate = '19700101';

        info.PatientsBirthDate = info.PatientBirthDate;
        info.PatientsSex = info.PatientSex;
        info.StudyDescription = '3DCS';
        info.PatientName.FamilyName = ['3DCS_rand_' num2str(randomization{1,2})];
             
        % LGE - save data
        dicomwrite(data,[pna '\' fn{l}(end-7:end) '.dcm'],info,'IOD','MR Image Storage');
        
        % clear variables
        clearvars info data
        
    end; clear l
    
    % clear variables
    clearvars fn
    
end; clear k


%% load, rename and save lge lax
for k = 1:length(lax_)
    
    fn = DicomInfo(lax_(k)).Filenames;
    
    for l = 1:length(fn)
        
        info = dicominfo(fn{l});
        data = dicomread(fn{l});

        % LGE - change DicomInfo for saving
        info.FileModDate = [];
        info.InstanceCreationDate = [];
        info.StudyDate = '19700101';
        info.SeriesDate = '19700101';
        info.AcquisitionDate = '19700101';
        info.ContentDate = '19700101';
        
        info.PatientsBirthDate = info.PatientBirthDate;
        info.PatientsSex = info.PatientSex;
        info.StudyDescription = '3DCS';
        info.PatientName.FamilyName = ['3DCS_rand_' num2str(randomization{1,2})];
             
        % LGE - save data
        dicomwrite(data,[pna '\' fn{l}(end-7:end) '.dcm'],info,'IOD','MR Image Storage');
        
        % clear variables
        clearvars info data
        
    end; clear l
    
    % clear variables
    clearvars fn
    
end; clear k

%% load, rename and save CS

fn = DicomInfo(cs_(1)).Filenames;

for l = 1:length(fn)

    info = dicominfo(fn{l});
    data = dicomread(fn{l});
 
    % LGE - change DicomInfo for saving
    info.FileModDate = [];
    info.InstanceCreationDate = [];
    info.StudyDate = '19710101';
    info.SeriesDate = '19710101';
    info.AcquisitionDate = '19710101';
    info.ContentDate = '19710101';
    
    info.PatientsBirthDate = info.PatientBirthDate;
    info.PatientsSex = info.PatientSex;
    info.StudyDescription = '3DCS';
    info.PatientName.FamilyName = ['3DCS_rand_' num2str(randomization{1,3})];

    % LGE - save data
    dicomwrite(data,[pnb '\' fn{l}(end-7:end) '.dcm'],info,'IOD','MR Image Storage');

    % clear variables
    clearvars info data

end; clear l

% clear variables
clearvars fn
 