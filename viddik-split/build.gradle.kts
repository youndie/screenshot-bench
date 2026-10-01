plugins {
    alias(libs.plugins.kotlin.jvm)
    alias(libs.plugins.kotlin.compose)
    alias(libs.plugins.compose.multiplatform)
    alias(libs.plugins.ksp)
    alias(libs.plugins.viddik)
}

// viddik with no main sources: the fixtures sit in src/test and draw components from :components.
// The layout of youndie/viddik#53, where a snapshot of this module's own main classes has nothing
// to work on.
dependencies {
    implementation(project(":components"))
    implementation(compose.desktop.currentOs)
    implementation(libs.cmp.material3)
}

viddik {
    snapshotsDir = "build/goldens"
    providers.gradleProperty("benchForks").orNull?.let { shards = it.toInt() }
}

tasks.withType<Test>().configureEach {
    inputs.property("benchRun", providers.gradleProperty("benchRun").orElse("0"))
}
