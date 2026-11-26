package com.elitex.api;

/**
 * AntiElite: the termux-api package's binary (rewritten for AntiElite) sends to com.elitex.api/.TermuxApiReceiver, which
 * Android reads as this class name. This app's own Java package stays com.termux.api.
 */
public class TermuxApiReceiver extends com.termux.api.TermuxApiReceiver {
}
