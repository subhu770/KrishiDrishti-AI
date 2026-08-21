import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  Image,
  ScrollView,
  TextInput,
  ActivityIndicator,
  SafeAreaView,
  Platform,
  Dimensions,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import * as ImagePicker from 'expo-image-picker';
import { Audio } from 'expo-av';

const { width } = Dimensions.get('window');

const translations = {
  en: {
    title: "KrishiDrishti AI",
    subtitle: "Odisha Precision AgTech Engine",
    telemetry: "Microclimate Telemetry",
    temp: "Temperature",
    hum: "Relative Humidity",
    scanner: "Crop Leaf Scanner",
    selectImg: "Gallery Photo",
    takePhoto: "Camera Photo",
    btnDiagnose: "Initiate Precision Diagnosis",
    btnAnalyzing: "Analyzing Crop Matrix...",
    report: "AI Diagnostic Report",
    confidence: "Confidence",
    advisory: "Odia Voice Advisory",
    chemical: "🧪 Chemical Dosage / Acre",
    organic: "🌿 Organic Alternative",
    standby: "System Ready for Leaf Input",
    standbyDesc: "Provide leaf photography and specify weather telemetry to calculate infection risk scores, disease conditions, and crop therapies.",
    ipLabel: "FastAPI Backend API URL",
    highRisk: "HIGH OUTBREAK RISK",
    modRisk: "MODERATE OUTBREAK RISK",
    lowRisk: "LOW OUTBREAK RISK",
    audioPlaying: "Playing voice advisory...",
    audioPaused: "Voice advisory paused",
  },
  or: {
    title: "କୃଷିଦୃଷ୍ଟି AI",
    subtitle: "ଓଡ଼ିଶା ପ୍ରିସିସନ୍ ଏଗ୍ରିଟେକ୍ ଇଞ୍ଜିନ୍",
    telemetry: "ମାଇକ୍ରୋକ୍ଲାଇମେଟ୍ ଟେଲିମେଟ୍ରି",
    temp: "ତାପମାତ୍ରା",
    hum: "ଆପେକ୍ଷିକ ଆର୍ଦ୍ରତା",
    scanner: "ଫସଲ ପତ୍ର ସ୍କାନର୍",
    selectImg: "ଗ୍ୟାଲେରୀ ଫଟୋ",
    takePhoto: "କ୍ୟାମେରା ଫଟୋ",
    btnDiagnose: "ପ୍ରିସିସନ୍ ନିରୂପଣ ଆରମ୍ଭ କରନ୍ତୁ",
    btnAnalyzing: "ଫସଲ ମ୍ୟାଟ୍ରିକ୍ସ ବିଶ୍ଳେଷଣ...",
    report: "AI ରୋଗ ନିରୂପଣ ରିପୋର୍ଟ",
    confidence: "ଆତ୍ମବିଶ୍ୱାସ ସ୍ତର",
    advisory: "ଓଡ଼ିଆ ଭାଷା ପରାମର୍ଶ (ଶବ୍ଦ/ଲେଖା)",
    chemical: "🧪 ରାସାୟନିକ ମାତ୍ରା / ଏକର",
    organic: "🌿 ଜୈବିକ ବିକଳ୍ପ",
    standby: "ସିଷ୍ଟମ ପ୍ରସ୍ତୁତ ଅଛି",
    standbyDesc: "ରୋଗ ନିରୂପଣ ଏବଂ ଉପଚାର ପାଇଁ ମୋବାଇଲ କ୍ୟାମେରା ଦ୍ଵାରା ପତ୍ରର ଫଟୋ ଉଠାନ୍ତୁ ଏବଂ ପାଣିପାଗ ସୂଚନା ଦିଅନ୍ତୁ।",
    ipLabel: "ସର୍ଭର API URL",
    highRisk: "ଉଚ୍ଚ ସଂକ୍ରମଣ ଆଶଙ୍କା ⚠️",
    modRisk: "ମଧ୍ୟମ ସଂକ୍ରମଣ ଆଶଙ୍କା ⚡",
    lowRisk: "କମ୍ ସଂକ୍ରମଣ ଆଶଙ୍କା ✅",
    audioPlaying: "ପରାମର୍ଶ ଶୁଣନ୍ତୁ...",
    audioPaused: "ପରାମର୍ଶ ବନ୍ଦ ଅଛି",
  },
  hi: {
    title: "कृषिदृष्टि AI",
    subtitle: "ओडिशा प्रिसिजन एग्रिटेक इंजन",
    telemetry: "माइक्रोक्लाइमेट टेलीमेट्री",
    temp: "तापमान",
    hum: "सापेक्ष आर्द्रता",
    scanner: "फसल पत्ता स्कैनर",
    selectImg: "गैलरी फोटो",
    takePhoto: "कैमरा फोटो",
    btnDiagnose: "सटीक निदान शुरू करें",
    btnAnalyzing: "फसल मैट्रिक्स विश्लेषण...",
    report: "AI रोग निदान रिपोर्ट",
    confidence: "आत्मविश्वास स्कोर",
    advisory: "आवाज और पाठ सलाह",
    chemical: "🧪 रासायनिक खुराक / एकड़",
    organic: "🌿 जैविक विकल्प",
    standby: "प्रणाली तैयार है",
    standbyDesc: "रोग निदान और उपचार के लिए मोबाइल कैमरा द्वारा पत्ते की फोटो लें और मौसम की जानकारी दें।",
    ipLabel: "सर्वर एपीआई यूआरएल",
    highRisk: "उच्च संक्रमण का खतरा ⚠️",
    modRisk: "मध्यम संक्रमण का खतरा ⚡",
    lowRisk: "कम संक्रमण का खतरा ✅",
    audioPlaying: "सलाह चल रही है...",
    audioPaused: "सलाह रुकी हुई है",
  }
};

export default function App() {
  const [lang, setLang] = useState('en');
  const [temp, setTemp] = useState(28);
  const [humidity, setHumidity] = useState(85);
  const [imageUri, setImageUri] = useState(null);
  
  // React Native loopback default: 10.0.2.2 works on Android emulator, 127.0.0.1 on iOS simulator
  const [apiBaseUrl, setApiBaseUrl] = useState(
    Platform.OS === 'android' ? 'http://10.0.2.2:8000' : 'http://127.0.0.1:8000'
  );
  
  const [isLoading, setIsLoading] = useState(false);
  const [resultData, setResultData] = useState(null);

  // Audio Playback states
  const [sound, setSound] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioDuration, setAudioDuration] = useState(0);
  const [audioPosition, setAudioPosition] = useState(0);

  const t = (key) => translations[lang][key] || key;

  // Custom Playback status callback
  const onPlaybackStatusUpdate = (status) => {
    if (status.isLoaded) {
      setAudioPosition(status.positionMillis);
      setAudioDuration(status.durationMillis);
      setIsPlaying(status.isPlaying);
      
      if (status.didJustFinish) {
        setIsPlaying(false);
        setAudioPosition(0);
      }
    }
  };

  const setupAudio = async (url) => {
    try {
      if (sound) {
        await sound.unloadAsync();
      }
      const { sound: newSound } = await Audio.Sound.createAsync(
        { uri: url },
        { shouldPlay: false },
        onPlaybackStatusUpdate
      );
      setSound(newSound);
    } catch (e) {
      console.warn("Error setting up audio:", e);
    }
  };

  const playPauseAudio = async () => {
    if (!sound) return;
    try {
      if (isPlaying) {
        await sound.pauseAsync();
      } else {
        await sound.playAsync();
      }
    } catch (e) {
      console.warn("Error toggling audio:", e);
    }
  };

  // Cleanup audio on component unmount
  useEffect(() => {
    return sound
      ? () => {
          sound.unloadAsync();
        }
      : undefined;
  }, [sound]);

  // Request gallery permissions
  const pickImage = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      alert('Sorry, we need library permissions to pick crop leaf photos.');
      return;
    }
    
    let result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.8,
    });

    if (!result.canceled) {
      setImageUri(result.assets[0].uri);
      // Reset old result cards
      setResultData(null);
      if (sound) {
        await sound.unloadAsync();
        setSound(null);
      }
    }
  };

  // Request camera permissions
  const takePhoto = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      alert('Sorry, we need camera permissions to capture crop leaf photos.');
      return;
    }

    let result = await ImagePicker.launchCameraAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.8,
    });

    if (!result.canceled) {
      setImageUri(result.assets[0].uri);
      // Reset old result cards
      setResultData(null);
      if (sound) {
        await sound.unloadAsync();
        setSound(null);
      }
    }
  };

  const removeImage = async () => {
    setImageUri(null);
    setResultData(null);
    if (sound) {
      await sound.unloadAsync();
      setSound(null);
    }
    setIsPlaying(false);
    setAudioPosition(0);
  };

  const diagnoseLeaf = async () => {
    if (!imageUri) return;
    setIsLoading(true);
    setResultData(null);

    try {
      const formData = new FormData();
      
      const uriParts = imageUri.split('/');
      const fileName = uriParts[uriParts.length - 1];
      const fileType = fileName.split('.').pop();
      
      formData.append('file', {
        uri: Platform.OS === 'ios' ? imageUri.replace('file://', '') : imageUri,
        name: fileName,
        type: `image/${fileType === 'jpg' ? 'jpeg' : fileType}`,
      });
      formData.append('temperature', temp.toString());
      formData.append('humidity', humidity.toString());

      const response = await fetch(`${apiBaseUrl}/api/v1/diagnose`, {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'multipart/form-data',
        },
      });

      if (!response.ok) {
        throw new Error(`Diagnosis endpoint error: Code ${response.status}`);
      }

      const resJson = await response.json();
      if (resJson.status === 'success') {
        setResultData(resJson.data);
        if (resJson.data.audio_url) {
          // Point audio url back to our FastAPI backend
          setupAudio(`${apiBaseUrl}${resJson.data.audio_url}`);
        }
      } else {
        alert('Engine diagnosis failed.');
      }
    } catch (err) {
      console.warn(err);
      alert('Network Error: Verify that backend server is active and API URL is correct.');
    } finally {
      setIsLoading(false);
    }
  };

  // Helper formatting for audio player times
  const formatTime = (millis) => {
    if (isNaN(millis)) return "00:00";
    const minutes = Math.floor(millis / 60000);
    const seconds = ((millis % 60000) / 1000).toFixed(0);
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="light" />
      
      {/* Header bar */}
      <View style={styles.header}>
        <View style={styles.headerLogoContainer}>
          <Text style={styles.headerTitle}>{t('title')}</Text>
          <Text style={styles.headerSubtitle}>{t('subtitle')}</Text>
        </View>
        
        {/* Multilingual Selector */}
        <View style={styles.langSelector}>
          {['en', 'or', 'hi'].map((l) => (
            <TouchableOpacity
              key={l}
              onPress={() => setLang(l)}
              style={[styles.langBtn, lang === l && styles.langBtnActive]}
            >
              <Text style={[styles.langBtnText, lang === l && styles.langBtnTextActive]}>
                {l.toUpperCase()}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContainer} keyboardShouldPersistTaps="handled">
        
        {/* Server Endpoint Config Input */}
        <View style={styles.card}>
          <Text style={styles.inputLabel}>{t('ipLabel')}</Text>
          <TextInput
            style={styles.textInput}
            value={apiBaseUrl}
            onChangeText={setApiBaseUrl}
            placeholder="http://10.0.2.2:8000"
            placeholderTextColor="#64748b"
            autoCapitalize="none"
            autoCorrect={false}
          />
        </View>

        {/* Microclimate Inputs Card */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>{t('telemetry')}</Text>
          
          {/* Temperature */}
          <View style={styles.telemetryRow}>
            <View>
              <Text style={styles.telemetryLabel}>{t('temp')}</Text>
              <Text style={styles.telemetrySubLabel}>Range: 15°C - 45°C</Text>
            </View>
            <View style={styles.stepControls}>
              <TouchableOpacity 
                onPress={() => setTemp(Math.max(15, temp - 1))} 
                style={styles.stepBtn}
              >
                <Text style={styles.stepBtnText}>-</Text>
              </TouchableOpacity>
              <Text style={styles.telemetryValue}>{temp}°C</Text>
              <TouchableOpacity 
                onPress={() => setTemp(Math.min(45, temp + 1))} 
                style={styles.stepBtn}
              >
                <Text style={styles.stepBtnText}>+</Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* Humidity */}
          <View style={styles.telemetryRow}>
            <View>
              <Text style={styles.telemetryLabel}>{t('hum')}</Text>
              <Text style={styles.telemetrySubLabel}>Range: 30% - 100%</Text>
            </View>
            <View style={styles.stepControls}>
              <TouchableOpacity 
                onPress={() => setHumidity(Math.max(30, humidity - 5))} 
                style={styles.stepBtn}
              >
                <Text style={styles.stepBtnText}>-</Text>
              </TouchableOpacity>
              <Text style={styles.telemetryValue}>{humidity}%</Text>
              <TouchableOpacity 
                onPress={() => setHumidity(Math.min(100, humidity + 5))} 
                style={styles.stepBtn}
              >
                <Text style={styles.stepBtnText}>+</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>

        {/* Leaf Upload Scanner Card */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>{t('scanner')}</Text>
          
          <View style={styles.uploadZone}>
            {imageUri ? (
              <View style={styles.previewContainer}>
                <Image source={{ uri: imageUri }} style={styles.previewImage} />
                <TouchableOpacity onPress={removeImage} style={styles.removeImageBtn}>
                  <Text style={styles.removeImageBtnText}>✕</Text>
                </TouchableOpacity>
              </View>
            ) : (
              <View style={styles.uploadPlaceholder}>
                <Text style={styles.uploadPlaceholderText}>No image selected</Text>
              </View>
            )}
          </View>

          {/* Action capture buttons */}
          <View style={styles.captureRow}>
            <TouchableOpacity onPress={pickImage} style={styles.actionBtn}>
              <Text style={styles.actionBtnText}>🖼️ {t('selectImg')}</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={takePhoto} style={styles.actionBtn}>
              <Text style={styles.actionBtnText}>📷 {t('takePhoto')}</Text>
            </TouchableOpacity>
          </View>

          {/* Diagnosis trigger */}
          <TouchableOpacity
            onPress={diagnoseLeaf}
            disabled={!imageUri || isLoading}
            style={[
              styles.diagnoseBtn,
              (!imageUri || isLoading) && styles.diagnoseBtnDisabled
            ]}
          >
            {isLoading ? (
              <ActivityIndicator color="#080c14" />
            ) : (
              <Text style={styles.diagnoseBtnText}>🛡️ {t('btnDiagnose')}</Text>
            )}
          </TouchableOpacity>
        </View>

        {/* Results Panel */}
        <View style={[styles.card, styles.resultsCard]}>
          {resultData ? (
            <View style={styles.reportContainer}>
              <View style={styles.reportHeader}>
                <View>
                  <Text style={styles.badgeText}>DIAGNOSTIC COMPLETE</Text>
                  <Text style={styles.diagnosisTitle}>{resultData.diagnosis}</Text>
                  <Text style={styles.diagnosisOdia}>{resultData.odia_name}</Text>
                </View>
                <View style={styles.confidenceBadge}>
                  <Text style={styles.confBadgeLabel}>{t('confidence')}</Text>
                  <Text style={styles.confBadgeValue}>{resultData.confidence}%</Text>
                </View>
              </View>

              {/* Progress Confidence bar */}
              <View style={styles.progressBarBg}>
                <View 
                  style={[
                    styles.progressBarFill, 
                    { width: `${resultData.confidence}%` }
                  ]} 
                />
              </View>

              {/* Microclimate risk indicator */}
              {resultData.weather_risk && (
                <View 
                  style={[
                    styles.riskContainer,
                    resultData.weather_risk.level.includes('HIGH') && styles.riskHigh,
                    resultData.weather_risk.level.includes('MODERATE') && styles.riskModerate,
                    resultData.weather_risk.level.includes('LOW') && styles.riskLow,
                  ]}
                >
                  <Text 
                    style={[
                      styles.riskText,
                      resultData.weather_risk.level.includes('HIGH') && styles.riskTextHigh,
                      resultData.weather_risk.level.includes('MODERATE') && styles.riskTextMod,
                      resultData.weather_risk.level.includes('LOW') && styles.riskTextLow,
                    ]}
                  >
                    {resultData.weather_risk.level}
                  </Text>
                  <Text style={styles.riskDesc}>{resultData.weather_risk.message}</Text>
                </View>
              )}

              {/* Odia Audio and Text advisory */}
              <View style={styles.advisoryContainer}>
                <Text style={styles.advisoryHeader}>{t('advisory')}</Text>
                <Text style={styles.advisoryText}>{resultData.odia_advisory}</Text>
                
                {/* Audio controls */}
                {sound && (
                  <View style={styles.audioPlayer}>
                    <TouchableOpacity onPress={playPauseAudio} style={styles.playBtn}>
                      <Text style={styles.playBtnText}>{isPlaying ? "⏸️" : "▶️"}</Text>
                    </TouchableOpacity>
                    <View style={styles.audioTrackContainer}>
                      <Text style={styles.audioStatus}>
                        {isPlaying ? t('audioPlaying') : t('audioPaused')}
                      </Text>
                      <Text style={styles.audioTimer}>
                        {formatTime(audioPosition)} / {formatTime(audioDuration)}
                      </Text>
                    </View>
                  </View>
                )}
              </View>

              {/* Treatment dosage columns */}
              <View style={styles.dosageRow}>
                <View style={[styles.dosageBox, styles.dosageChem]}>
                  <Text style={styles.dosageHeader}>{t('chemical')}</Text>
                  <Text style={styles.dosageContent}>{resultData.chemical_dosage}</Text>
                </View>
                <View style={[styles.dosageBox, styles.dosageOrg]}>
                  <Text style={styles.dosageHeader}>{t('organic')}</Text>
                  <Text style={styles.dosageContent}>{resultData.organic_solution}</Text>
                </View>
              </View>
            </View>
          ) : (
            <View style={styles.standbyContainer}>
              <View style={styles.standbyIconContainer}>
                <Text style={styles.standbyIcon}>🌾</Text>
              </View>
              <Text style={styles.standbyTitle}>{t('standby')}</Text>
              <Text style={styles.standbyDesc}>{t('standbyDesc')}</Text>
            </View>
          )}
        </View>

      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#080c14',
  },
  scrollContainer: {
    padding: 16,
    paddingBottom: 40,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 255, 255, 0.05)',
    backgroundColor: '#05070a',
  },
  headerLogoContainer: {
    flex: 1,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: '900',
    color: '#10b981',
  },
  headerSubtitle: {
    fontSize: 9,
    fontWeight: 'bold',
    color: '#94a3b8',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  langSelector: {
    flexDirection: 'row',
    backgroundColor: '#0f172a',
    borderRadius: 8,
    padding: 2,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)',
  },
  langBtn: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  langBtnActive: {
    backgroundColor: '#10b981',
  },
  langBtnText: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#64748b',
  },
  langBtnTextActive: {
    color: '#080c14',
  },
  card: {
    backgroundColor: 'rgba(15, 23, 42, 0.45)',
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.08)',
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#f8fafc',
    marginBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.05)',
    paddingBottom: 6,
  },
  inputLabel: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#94a3b8',
    marginBottom: 8,
  },
  textInput: {
    backgroundColor: '#090d16',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.08)',
    borderRadius: 8,
    color: '#f8fafc',
    paddingHorizontal: 12,
    paddingVertical: 8,
    fontSize: 14,
  },
  telemetryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  telemetryLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#cbd5e1',
  },
  telemetrySubLabel: {
    fontSize: 10,
    color: '#64748b',
  },
  stepControls: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  stepBtn: {
    width: 32,
    height: 32,
    backgroundColor: '#1e293b',
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.08)',
  },
  stepBtnText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#f8fafc',
  },
  telemetryValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#10b981',
    width: 60,
    textAlign: 'center',
  },
  uploadZone: {
    height: 200,
    borderWidth: 2,
    borderStyle: 'dashed',
    borderColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: 12,
    backgroundColor: 'rgba(5, 7, 10, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    overflow: 'hidden',
  },
  uploadPlaceholder: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  uploadPlaceholderText: {
    color: '#64748b',
    fontSize: 14,
  },
  previewContainer: {
    width: '100%',
    height: '100%',
    position: 'relative',
  },
  previewImage: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  removeImageBtn: {
    position: 'absolute',
    top: 8,
    right: 8,
    backgroundColor: 'rgba(0,0,0,0.6)',
    width: 28,
    height: 28,
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
  },
  removeImageBtnText: {
    color: '#ef4444',
    fontWeight: 'bold',
    fontSize: 12,
  },
  captureRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 12,
    marginTop: 12,
  },
  actionBtn: {
    flex: 1,
    backgroundColor: '#0f172a',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)',
    borderRadius: 8,
    paddingVertical: 10,
    alignItems: 'center',
  },
  actionBtnText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#e2e8f0',
  },
  diagnoseBtn: {
    backgroundColor: '#10b981',
    borderRadius: 10,
    paddingVertical: 14,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 16,
  },
  diagnoseBtnDisabled: {
    backgroundColor: '#1e293b',
  },
  diagnoseBtnText: {
    color: '#080c14',
    fontSize: 14,
    fontWeight: 'bold',
  },
  resultsCard: {
    minHeight: 160,
  },
  standbyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 20,
  },
  standbyIconContainer: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: 'rgba(16, 185, 129, 0.08)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  standbyIcon: {
    fontSize: 24,
  },
  standbyTitle: {
    fontSize: 15,
    fontWeight: 'bold',
    color: '#e2e8f0',
  },
  standbyDesc: {
    fontSize: 11,
    color: '#64748b',
    textAlign: 'center',
    marginTop: 4,
    lineHeight: 16,
  },
  reportContainer: {
    width: '100%',
  },
  reportHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  badgeText: {
    fontSize: 8,
    fontWeight: '900',
    color: '#10b981',
    letterSpacing: 1,
    marginBottom: 4,
  },
  diagnosisTitle: {
    fontSize: 18,
    fontWeight: '900',
    color: '#f8fafc',
  },
  diagnosisOdia: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#2dd4bf',
    marginTop: 2,
  },
  confidenceBadge: {
    backgroundColor: '#090d16',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)',
    borderRadius: 8,
    paddingHorizontal: 8,
    paddingVertical: 4,
    alignItems: 'center',
  },
  confBadgeLabel: {
    fontSize: 8,
    color: '#94a3b8',
    fontWeight: 'bold',
    textTransform: 'uppercase',
  },
  confBadgeValue: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#10b981',
    marginTop: 1,
  },
  progressBarBg: {
    height: 6,
    backgroundColor: '#090d16',
    borderRadius: 3,
    width: '100%',
    overflow: 'hidden',
    marginBottom: 16,
  },
  progressBarFill: {
    height: '100%',
    backgroundColor: '#10b981',
    borderRadius: 3,
  },
  riskContainer: {
    borderWidth: 1,
    borderRadius: 10,
    padding: 12,
    marginBottom: 16,
  },
  riskHigh: {
    backgroundColor: 'rgba(239, 68, 68, 0.05)',
    borderColor: 'rgba(239, 68, 68, 0.15)',
  },
  riskModerate: {
    backgroundColor: 'rgba(245, 158, 11, 0.05)',
    borderColor: 'rgba(245, 158, 11, 0.15)',
  },
  riskLow: {
    backgroundColor: 'rgba(16, 185, 129, 0.05)',
    borderColor: 'rgba(16, 185, 129, 0.15)',
  },
  riskText: {
    fontSize: 12,
    fontWeight: 'bold',
  },
  riskTextHigh: {
    color: '#ef4444',
  },
  riskTextMod: {
    color: '#f59e0b',
  },
  riskTextLow: {
    color: '#10b981',
  },
  riskDesc: {
    fontSize: 10,
    color: '#cbd5e1',
    marginTop: 4,
    lineHeight: 14,
  },
  advisoryContainer: {
    backgroundColor: 'rgba(9,13,22,0.6)',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.04)',
    borderRadius: 10,
    padding: 12,
    marginBottom: 16,
  },
  advisoryHeader: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#94a3b8',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: 6,
  },
  advisoryText: {
    fontSize: 14,
    color: '#f1f5f9',
    lineHeight: 20,
    marginBottom: 12,
  },
  audioPlayer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#090d16',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)',
    borderRadius: 8,
    padding: 8,
  },
  playBtn: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#10b981',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 10,
  },
  playBtnText: {
    fontSize: 14,
  },
  audioTrackContainer: {
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  audioStatus: {
    fontSize: 11,
    color: '#e2e8f0',
    fontWeight: '600',
  },
  audioTimer: {
    fontSize: 10,
    fontFamily: Platform.OS === 'ios' ? 'Courier' : 'monospace',
    color: '#94a3b8',
  },
  dosageRow: {
    flexDirection: 'row',
    gap: 12,
  },
  dosageBox: {
    flex: 1,
    borderRadius: 10,
    padding: 10,
    borderWidth: 1,
  },
  dosageChem: {
    backgroundColor: 'rgba(59, 130, 246, 0.05)',
    borderColor: 'rgba(59, 130, 246, 0.15)',
  },
  dosageOrg: {
    backgroundColor: 'rgba(16, 185, 129, 0.05)',
    borderColor: 'rgba(16, 185, 129, 0.15)',
  },
  dosageHeader: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#f8fafc',
    marginBottom: 6,
  },
  dosageContent: {
    fontSize: 10,
    color: '#cbd5e1',
    lineHeight: 14,
  },
});
