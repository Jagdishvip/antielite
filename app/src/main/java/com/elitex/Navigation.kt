package com.elitex

import androidx.compose.runtime.Composable
import com.elitex.ui.chat.ChatScreen
import com.elitex.ui.chat.ChatViewModel

@Composable
fun MainNavigation(viewModel: ChatViewModel? = null) {
    if (viewModel != null) {
        ChatScreen(viewModel = viewModel)
    } else {
        ChatScreen()
    }
}
