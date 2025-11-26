"use client";

import React, { useState } from "react";


interface ChatMessage {
  role: "user" | "assistant";
  text: string;
  imageBase64?: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

const TOPS = [
  { src: `${API_BASE}/images/Tops/hoodie1.jpg`, label: "Red hoodie" },
  { src: `${API_BASE}/images/Tops/hoodie2.jpg`, label: "Brown hoodie" },
  { src: `${API_BASE}/images/Tops/jacket1.jpg`, label: "Black jacket" },
  { src: `${API_BASE}/images/Tops/sweater1.jpg`, label: "Grey sweater" },
  { src: `${API_BASE}/images/Tops/polo1.jpg`, label: "Black polo" },
  { src: `${API_BASE}/images/Tops/polo2.jpg`, label: "Green polo" },
  { src: `${API_BASE}/images/Tops/polo3.jpg`, label: "Blue polo" },
];

const BOTTOMS = [
  { src: `${API_BASE}/images/Bottoms/jeans1.jpg`, label: "Black jeans" },
  { src: `${API_BASE}/images/Bottoms/jeans2.jpg`, label: "Blue jeans" },
  { src: `${API_BASE}/images/Bottoms/jeans3.jpg`, label: "Slim black jeans" },
  { src: `${API_BASE}/images/Bottoms/lightwashjeans.jpg`, label: "Light wash jeans" },
  { src: `${API_BASE}/images/Bottoms/graysweats.jpg`, label: "Grey sweats" },
  { src: `${API_BASE}/images/Bottoms/A46740001-front-gstk.jpeg`, label: "Khaki chinos" }
];

export default function HomePage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [prompt, setPrompt] = useState("");
  const [file, setFile] = useState<File | null>(null); // per-request override image
  const [isLoading, setIsLoading] = useState(false);

  // Base / profile image state
  const [profileImageFile, setProfileImageFile] = useState<File | null>(null);
  const [hasProfileImage, setHasProfileImage] = useState(false);
  const [profilePreviewUrl, setProfilePreviewUrl] = useState<string | null>(null);

  const handleSaveProfileImage = async () => {
    if (!profileImageFile) return;

    const formData = new FormData();
    formData.append("image", profileImageFile);

    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

      const res = await fetch(`${API_BASE}/api/upload-person-image`, {
        method: "POST",
        body: formData,
        });

      const data = await res.json();

      if (data.success) {
        setHasProfileImage(true);
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            text: "Your base photo has been saved ✅",
          },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            text: `Error saving profile image: ${data.error || "Unknown error"}`,
          },
        ]);
      }
    } catch (err: any) {
      console.error("PROFILE UPLOAD ERROR:", err);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: `Failed to upload profile image: ${err.message}`,
        },
      ]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // Need a prompt
    if (!prompt) return;
    // Need either a per-request file or a saved base photo
    if (!file && !hasProfileImage) return;

    // Add user message
    setMessages((prev) => [...prev, { role: "user", text: prompt }]);
    setIsLoading(true);

    try {
      const formData = new FormData();
      formData.append("prompt", prompt);

      // Only append an image if user selected one for this request.
      // If not, backend will use the saved profile image.
      if (file) {
        formData.append("image", file);
      }

      const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

      const res = await fetch(`${API_BASE}/api/generate-outfit`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (!data.success) {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", text: `Error: ${data.error || "Unknown error"}` },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            text: "Here is your styled outfit 😎",
            imageBase64: data.image_base64,
          },
        ]);
      }
    } catch (err: any) {
      console.error("FETCH ERROR:", err);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: `Request failed: ${err.message}` },
      ]);
    } finally {
      setIsLoading(false);
      setPrompt("");
      setFile(null);
    }
  };

  return (
    <div className="min-h-screen bg-[#f7f3ef] text-slate-900 flex justify-center">
      <div className="w-full max-w-3xl p-6">
        {/* Header */}
        <header className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-semibold tracking-tight text-[#1f2933]">
              AI Outfit Stylist
            </h1>
            <p className="text-xs mt-1 text-slate-500 uppercase tracking-[0.18em]">
              curated looks · personal moodboard
            </p>
          </div>
          <div className="hidden sm:flex items-center gap-2 text-xs text-slate-500">
            <span className="inline-block h-2 w-2 rounded-full bg-emerald-400" />
            <span>Stylist online</span>
          </div>
        </header>

        {/* Closet preview */}
<section className="mb-6 space-y-4">
  <div>
    <h2 className="text-sm font-medium text-[#2f3437]">Your Closet</h2>
    <p className="text-xs text-slate-500">
      A quick view of the pieces your stylist can pull from.
    </p>
  </div>

  {/* Tops row */}
  <div>
    <h3 className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500 mb-2">
      Tops
    </h3>
    <div className="flex gap-3 overflow-x-auto pb-1">
      {TOPS.map((item, idx) => (
        <div
          key={idx}
          className="min-w-[90px] max-w-[90px] flex-shrink-0 rounded-2xl bg-white border border-[#e2d6c8] shadow-sm overflow-hidden"
        >
          <img
            src={item.src}
            alt={item.label}
            className="h-20 w-full object-cover"
          />
          <div className="px-2 py-1.5">
            <p className="text-[10px] font-medium text-[#2f3437] truncate">
              {item.label}
            </p>
            <p className="text-[9px] text-slate-400">Top</p>
          </div>
        </div>
      ))}
    </div>
  </div>

  {/* Bottoms row */}
  <div>
    <h3 className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500 mb-2">
      Bottoms
    </h3>
    <div className="flex gap-3 overflow-x-auto pb-1">
      {BOTTOMS.map((item, idx) => (
        <div
          key={idx}
          className="min-w-[90px] max-w-[90px] flex-shrink-0 rounded-2xl bg-white border border-[#e2d6c8] shadow-sm overflow-hidden"
        >
          <img
            src={item.src}
            alt={item.label}
            className="h-20 w-full object-cover"
          />
          <div className="px-2 py-1.5">
            <p className="text-[10px] font-medium text-[#2f3437] truncate">
              {item.label}
            </p>
            <p className="text-[9px] text-slate-400">Bottom</p>
          </div>
        </div>
      ))}
    </div>
  </div>
</section>

        {/* Base / Profile Photo Section */}
        <div className="mb-6 border border-[#e2d6c8] rounded-2xl p-4 bg-white/70 shadow-sm backdrop-blur">
          <h2 className="text-sm font-medium text-[#2f3437] mb-1">
            Your Base Photo
          </h2>
          <p className="text-xs text-slate-500 mb-3">
            Upload a clear photo of yourself once. We&apos;ll reuse it for future looks
            unless you override it with a new image.
          </p>

          <div className="flex flex-col sm:flex-row sm:items-center gap-4">
            {profilePreviewUrl && (
              <img
                src={profilePreviewUrl}
                alt="Profile preview"
                className="rounded-2xl border border-[#e2d6c8] max-w-[140px] shadow-sm object-cover"
              />
            )}

            <div className="flex-1 space-y-2">
              <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
                <input
                  type="file"
                  accept="image/*"
                  className="text-xs file:mr-3 file:rounded-full file:border-0 file:bg-[#f3e3d5] file:px-3 file:py-1.5 file:text-xs file:font-medium file:text-[#4b3b34] hover:file:bg-[#e8d4c0]"
                  onChange={(e) => {
                    const f = e.target.files?.[0] || null;
                    setProfileImageFile(f);
                    if (f) {
                      setProfilePreviewUrl(URL.createObjectURL(f));
                    } else {
                      setProfilePreviewUrl(null);
                    }
                  }}
                />
                <button
                  type="button"
                  onClick={handleSaveProfileImage}
                  disabled={!profileImageFile}
                  className="inline-flex items-center justify-center rounded-full px-4 py-1.5 text-xs font-medium border border-[#e2d6c8] text-[#4b3b34] bg-[#f9f4ee] disabled:opacity-50 hover:bg-[#f1e3d6] transition-colors"
                >
                  Save Base Photo
                </button>
              </div>

              {hasProfileImage && (
                <p className="text-xs text-emerald-600 flex items-center gap-1">
                  <span className="inline-block h-1.5 w-1.5 rounded-full bg-emerald-500" />
                  Base photo saved. You can now generate outfits with just a prompt.
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Chat box */}
        <div className="border border-[#e2d6c8] rounded-2xl p-4 h-96 overflow-y-auto mb-4 bg-white/80 shadow-sm backdrop-blur-sm">
          {messages.map((m, idx) => (
            <div
              key={idx}
              className={`mb-3 flex ${
                m.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`px-3 py-2 rounded-2xl max-w-xs text-sm leading-relaxed shadow-sm ${
                  m.role === "user"
                    ? "bg-[#1f2933] text-white rounded-br-sm"
                    : "bg-[#f6eee6] text-[#2f3437] rounded-bl-sm border border-[#eadac8]"
                }`}
              >
                <p>{m.text}</p>
                {m.imageBase64 && (
                  <img
                    src={`data:image/png;base64,${m.imageBase64}`}
                    alt="Generated outfit"
                    className="mt-2 rounded-2xl border border-white/60 shadow-sm max-w-xs"
                  />
                )}
              </div>
            </div>
          ))}
          {isLoading && (
            <p className="text-xs text-slate-500 italic">Styling your look…</p>
          )}
        </div>

        {/* Input form */}
        <form onSubmit={handleSubmit} className="space-y-3">
          <label className="block text-xs font-medium text-slate-600 mb-1">
            Describe your vibe
          </label>
          <textarea
            className="w-full p-3 rounded-2xl bg-white border border-[#e2d6c8] text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#e9c7a8] focus:border-transparent transition-shadow shadow-sm"
            placeholder="e.g., Dark and casual for fall, something I can wear to a coffee date."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
          />

          <div className="space-y-2">
            <label className="text-xs text-slate-500">
              Optional: upload a new image for this request (otherwise your saved base
              photo is used)
            </label>
            <input
              type="file"
              accept="image/*"
              className="text-xs file:mr-3 file:rounded-full file:border-0 file:bg-[#f3e3d5] file:px-3 file:py-1.5 file:text-xs file:font-medium file:text-[#4b3b34] hover:file:bg-[#e8d4c0]"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
            />
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={isLoading || !prompt || (!file && !hasProfileImage)}
              className="inline-flex items-center justify-center rounded-full px-5 py-2 text-sm font-medium bg-[#1f2933] text-white disabled:bg-slate-400 shadow-sm hover:bg-[#111827] transition-colors"
            >
              {isLoading ? "Styling..." : "Send to Stylist"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}