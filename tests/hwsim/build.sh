#!/bin/sh

set -e

cd $(dirname $0)

cd ../../wpa_supplicant
cp ../tests/hwsim/example-wpa_supplicant.config .config
make clean
make -j8
cd ../hostapd
cp ../tests/hwsim/example-hostapd.config .config
make clean
make -j8 hostapd hlr_auc_gw
cd ../wlantest
make clean
make -j8
cd ../mac80211_hwsim/tools
make -j8