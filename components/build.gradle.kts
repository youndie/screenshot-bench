plugins {
    alias(libs.plugins.kotlin.multiplatform)
    alias(libs.plugins.kotlin.compose)
    alias(libs.plugins.compose.multiplatform)
}

// The components as a separate KMP module, the way a multi-module app keeps them: `viddik-split`
// renders them from its test source set alone and sees them only as this module's jvm jar.
kotlin {
    jvm()
    sourceSets {
        jvmMain {
            kotlin.srcDir("../fixtures/src")
            dependencies {
                implementation(libs.cmp.runtime)
                implementation(libs.cmp.foundation)
                implementation(libs.cmp.material3)
            }
        }
    }
}
