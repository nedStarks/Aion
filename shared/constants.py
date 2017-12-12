#!/usr/bin/python

keyEvents = ["KEYCODE_UNKNOWN", "KEYCODE_MENU", "KEYCODE_SOFT_RIGHT", "KEYCODE_HOME", "KEYCODE_BACK", "KEYCODE_CALL", "KEYCODE_ENDCALL", "KEYCODE_0", "KEYCODE_1", "KEYCODE_2", "KEYCODE_3", "KEYCODE_4", "KEYCODE_5", "KEYCODE_6", "KEYCODE_7", "KEYCODE_8", "KEYCODE_9", "KEYCODE_STAR", "KEYCODE_POUND", "KEYCODE_DPAD_UP", "KEYCODE_DPAD_DOWN", "KEYCODE_DPAD_LEFT", "KEYCODE_DPAD_RIGHT", "KEYCODE_DPAD_CENTER", "KEYCODE_VOLUME_UP", "KEYCODE_VOLUME_DOWN", "KEYCODE_POWER", "KEYCODE_CAMERA", "KEYCODE_CLEAR", "KEYCODE_A", "KEYCODE_B", "KEYCODE_C", "KEYCODE_D", "KEYCODE_E", "KEYCODE_F", "KEYCODE_G", "KEYCODE_H", "KEYCODE_I", "KEYCODE_J", "KEYCODE_K", "KEYCODE_L", "KEYCODE_M", "KEYCODE_N", "KEYCODE_O", "KEYCODE_P", "KEYCODE_Q", "KEYCODE_R", "KEYCODE_S", "KEYCODE_T", "KEYCODE_U", "KEYCODE_V", "KEYCODE_W", "KEYCODE_X", "KEYCODE_Y", "KEYCODE_Z", "KEYCODE_COMMA", "KEYCODE_PERIOD", "KEYCODE_ALT_LEFT", "KEYCODE_ALT_RIGHT", "KEYCODE_SHIFT_LEFT", "KEYCODE_SHIFT_RIGHT", "KEYCODE_TAB", "KEYCODE_SPACE", "KEYCODE_SYM", "KEYCODE_EXPLORER", "KEYCODE_ENVELOPE", "KEYCODE_ENTER", "KEYCODE_DEL", "KEYCODE_GRAVE", "KEYCODE_MINUS", "KEYCODE_EQUALS", "KEYCODE_LEFT_BRACKET", "KEYCODE_RIGHT_BRACKET", "KEYCODE_BACKSLASH", "KEYCODE_SEMICOLON", "KEYCODE_APOSTROPHE", "KEYCODE_SLASH", "KEYCODE_AT", "KEYCODE_NUM", "KEYCODE_HEADSETHOOK", "KEYCODE_FOCUS", "KEYCODE_PLUS", "KEYCODE_MENU", "KEYCODE_NOTIFICATION", "KEYCODE_SEARCH", "TAG_LAST_KEYCODE"]

keyEventTypes = ["DOWN", "UP", "DOWN_AND_UP"]

activityActions = ["touch", "type", "press", "drag"]

sensitiveAPICalls = {"android.content.ContextWrapper": ["bindService", "deleteDatabase", "deleteFile", "deleteSharedPreferences", "getSystemService", "openFileInput", "startService", "stopService", "unbindService", "unregisterReceiver"], "android.accounts.AccountManager": ["clearPassword", "getAccounts", "getPassword", "peekAuthToken", "setAuthToken", "setPassword"], "android.app.Activity": ["startActivity", "setContentView", "setVisible", "takeKeyEvents"], "android.app.DownloadManager": ["addCompletedDownload", "enqueue", "getUriForDownloadedFile", "openDownloadedFile", "query"], "android.app.IntentService": ["onStartCommand"], "android.content.ContentResolver": ["insert", "openFileDescriptor", "query", "update"], "android.content.pm.PackageInstaller": ["uninstall"], "android.database.sqlite.SQLiteDatabase": ["execSQL", "insert", "insertOrThrow", "openDatabase", "query", "rawQuery", "replace", "update"], "android.hardware.Camera": ["open", "reconnect", "release", "startPreview", "stopPreview", "takePicture"], "android.hardware.display.DisplayManager": ["getDisplay", "getDisplays"], "android.location.Location": ["getLatitude", "getLongitude"], "android.media.AudioRecord": ["read", "startRecording", "stop"], "android.media.MediaRecorder": ["prepare", "setCamera", "start", "stop"], "android.net.Network": ["bindSocket", "openConnection"], "android.net.NetworkInfo": ["isAvailable", "isConnected", "isRoaming"], "android.net.wifi.WifiInfo": ["getMacAddress", "getSSID"], "android.net.wifi.WifiManager": ["disconnect", "getScanResults", "getWifiState", "reconnect", "startScan"], "android.os.Process": ["killProcess"], "android.os.PowerManager": ["isInteractive", "isScreenOn", "reboot"], "android.telephony.SmsManager": ["sendDataMessage", "sendTextMessage"], "android.widget.Toast": ["makeText"], "dalvik.system.DexClassLoader": ["loadClass"], "dalvik.system.PathClassLoader": ["loadClass"], "java.lang.class": ["forName", "getClassLoader", "getClasses", "getField", "getFields", "getMethods", "getMethod", "getName"], "java.lang.reflect.Method": ["invoke"], "java.net.HttpCookie": ["getName", "getPath", "getSecure", "getValue", "parse", "setPath", "setSecure", "setValue"], "java.net.URL.openConnection": ["openConnection", "openStream"]}

droidmonDefaultClasses = [u'android.telephony.TelephonyManager', u'android.net.wifi.WifiInfo', u'android.os.Debug', u'android.app.SharedPreferencesImpl$EditorImpl', u'android.content.ContentValues', u'java.net.URL', u'org.apache.http.impl.client.AbstractHttpClient', u'android.app.ContextImpl', u'android.app.ActivityThread', u'android.app.Activity', u'dalvik.system.BaseDexClassLoader', u'dalvik.system.DexFile', u'dalvik.system.DexClassLoader', u'dalvik.system.PathClassLoader', u'java.lang.reflect.Method', u'javax.crypto.spec.SecretKeySpec', u'javax.crypto.Cipher', u'javax.crypto.Mac', u'android.app.ApplicationPackageManager', u'android.app.NotificationManager', u'android.util.Base64', u'android.net.ConnectivityManager', u'android.content.BroadcastReceiver', u'android.telephony.SmsManager', u'java.lang.Runtime', u'java.lang.ProcessBuilder', u'java.io.FileOutputStream', u'java.io.FileInputStream', u'android.app.ActivityManager', u'android.os.Process', u'android.content.ContentResolver', u'android.accounts.AccountManager', u'android.location.Location', u'android.media.AudioRecord', u'android.media.MediaRecorder', u'android.os.SystemProperties', u'libcore.io.IoBridge']

droidmonDefaultMethods = [u'getDeviceId', u'getSubscriberId', u'getLine1Number', u'getNetworkOperator', u'getNetworkOperatorName', u'getSimOperatorName', u'getMacAddress', u'getSimCountryIso', u'getSimSerialNumber', u'getNetworkCountryIso', u'getDeviceSoftwareVersion', u'isDebuggerConnected', u'putString', u'putBoolean', u'putInt', u'putLong', u'putFloat', u'put', u'openConnection', u'execute', u'registerReceiver', u'handleReceiver', u'startActivity', u'findResource', u'findLibrary', u'loadDex',u'findResources', u'loadClass', u'invoke', u'doFinal', u'setComponentEnabledSetting', u'notify', u'decode', u'listen', u'encode', u'encodeToString', u'setMobileDataEnabled', u'abortBroadcast', u'sendTextMessage', u'sendMultipartTextMessage', u'exec', u'start', u'write', u'read', u'killBackgroundProcesses', u'killProcess', u'query', u'registerContentObserver', u'insert', u'getAccountsByType', u'getAccounts', u'getLatitude', u'getLongitude', u'delete', u'startRecording', u'get', u'getInstalledPackages', u'open']

droidmonDefaultHooks = {u'android.accounts.AccountManager': [u'getAccountsByType', u'getAccounts'], u'android.app.Activity': [u'startActivity'], u'android.app.ActivityManager': [u'killBackgroundProcesses'], u'android.app.ActivityThread': [u'handleReceiver'], u'android.app.ApplicationPackageManager': [u'setComponentEnabledSetting',  u'getInstalledPackages'], u'android.app.ContextImpl': [u'registerReceiver'], u'android.app.NotificationManager': [u'notify'], u'android.app.SharedPreferencesImpl$EditorImpl': [u'putString', u'putBoolean', u'putInt', u'putLong', u'putFloat'], u'android.content.BroadcastReceiver': [u'abortBroadcast'], u'android.content.ContentResolver': [u'query', u'registerContentObserver', u'insert', u'delete'], u'android.content.ContentValues': [u'put'], u'android.location.Location': [u'getLatitude', u'getLongitude'], u'android.media.AudioRecord': [u'startRecording'], u'android.media.MediaRecorder': [u'start'], u'android.net.ConnectivityManager': [u'setMobileDataEnabled'], u'android.net.wifi.WifiInfo': [u'getMacAddress'], u'android.os.Debug': [u'isDebuggerConnected'], u'android.os.Process': [u'killProcess'], u'android.os.SystemProperties': [u'get'], u'android.telephony.SmsManager': [u'sendTextMessage', u'sendMultipartTextMessage'], u'android.telephony.TelephonyManager': [u'getDeviceId', u'getSubscriberId', u'getLine1Number', u'getNetworkOperator', u'getNetworkOperatorName', u'getSimOperatorName', u'getSimCountryIso', u'getSimSerialNumber', u'getNetworkCountryIso', u'getDeviceSoftwareVersion', u'listen'], u'android.util.Base64': [u'decode', u'encode', u'encodeToString'], u'dalvik.system.BaseDexClassLoader': [u'findResource', u'findLibrary', u'findResources'], u'dalvik.system.DexClassLoader': [], u'dalvik.system.DexFile': [u'loadDex', u'loadClass'], u'dalvik.system.PathClassLoader': [], u'java.io.FileInputStream': [u'read'], u'java.io.FileOutputStream': [u'write'], u'java.lang.ProcessBuilder': [u'start'], u'java.lang.Runtime': [u'exec'], u'java.lang.reflect.Method': [u'invoke'], u'java.net.URL': [u'openConnection'], u'javax.crypto.Cipher': [u'doFinal'], u'javax.crypto.Mac': [u'doFinal'], u'javax.crypto.spec.SecretKeySpec': [], u'libcore.io.IoBridge': [u'open'], u'org.apache.http.impl.client.AbstractHttpClient': [u'execute']}
