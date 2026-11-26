#![windows_subsystem = "windows"]

use std::io::{Read, Write};
use std::net::TcpStream;
use std::os::windows::process::CommandExt;
use std::process::{Child, Command};
use std::time::Duration;
use tao::dpi::LogicalSize;
use tao::event::{Event, WindowEvent};
use tao::event_loop::{ControlFlow, EventLoopBuilder};
use tao::window::WindowBuilder;
use wry::{WebContext, WebViewBuilder};

const PORT: u16 = 18765;
const OLLAMA_ADDR: &str = "127.0.0.1:18766";
const CREATE_NO_WINDOW: u32 = 0x0800_0000;
const LOADING: &str = "data:text/html,<body style='font-family:Segoe UI;background:%230f172a;color:%23e2e8f0;display:flex;align-items:center;justify-content:center;height:100vh;margin:0'><div>Starting AI Meeting Intelligence...</div></body>";

fn healthy() -> bool {
    let Ok(mut s) = TcpStream::connect_timeout(&format!("127.0.0.1:{PORT}").parse().unwrap(), Duration::from_millis(500)) else {
        return false;
    };
    let _ = s.set_read_timeout(Some(Duration::from_secs(2)));
    let _ = s.write_all(b"GET /health HTTP/1.0\r\nHost: localhost\r\n\r\n");
    let mut buf = String::new();
    let _ = s.read_to_string(&mut buf);
    buf.contains("200 OK")
}

fn app_dir() -> Option<std::path::PathBuf> {
    Some(std::env::current_exe().ok()?.parent()?.to_path_buf())
}

fn start_ollama() -> Option<Child> {
    let dir = app_dir()?;
    let exe = dir.join("ollama").join("ollama.exe");
    if !exe.is_file() {
        return None;
    }
    Command::new(exe)
        .arg("serve")
        .env("OLLAMA_HOST", OLLAMA_ADDR)
        .env("OLLAMA_MODELS", dir.join("ollama-models"))
        .env("OLLAMA_KEEP_ALIVE", "30m")
        .current_dir(&dir)
        .creation_flags(CREATE_NO_WINDOW)
        .spawn()
        .ok()
}

fn kill_tree(c: &mut Child) {
    let _ = Command::new("taskkill")
        .args(["/PID", &c.id().to_string(), "/T", "/F"])
        .creation_flags(CREATE_NO_WINDOW)
        .status();
    let _ = c.kill();
}

fn start_core(with_ollama: bool) -> Option<Child> {
    let dir = app_dir()?;
    let mut cmd = Command::new(dir.join("AIMeetingCore.exe"));
    if with_ollama {
        cmd.env("OLLAMA_HOST", OLLAMA_ADDR);
    }
    cmd.arg("--no-window")
        .env("PORT", PORT.to_string())
        .current_dir(&dir)
        .creation_flags(CREATE_NO_WINDOW)
        .spawn()
        .ok()
}

fn main() {
    let mut ollama = if healthy() { None } else { start_ollama() };
    let mut core = if healthy() { None } else { start_core(ollama.is_some()) };
    let event_loop = EventLoopBuilder::<()>::with_user_event().build();
    let proxy = event_loop.create_proxy();
    let window = WindowBuilder::new()
        .with_title("AI Meeting Intelligence")
        .with_inner_size(LogicalSize::new(1366.0, 860.0))
        .build(&event_loop)
        .unwrap();
    let data = std::env::var("LOCALAPPDATA").map(|d| std::path::PathBuf::from(d).join("AIMeeting").join("webview")).ok();
    let mut ctx = WebContext::new(data);
    let webview = WebViewBuilder::new_with_web_context(&mut ctx).with_url(LOADING).build(&window).unwrap();

    std::thread::spawn(move || {
        for _ in 0..180 {
            if healthy() {
                let _ = proxy.send_event(());
                return;
            }
            std::thread::sleep(Duration::from_secs(1));
        }
    });

    event_loop.run(move |event, _, flow| {
        *flow = ControlFlow::Wait;
        match event {
            Event::UserEvent(()) => {
                let _ = webview.load_url(&format!("http://127.0.0.1:{PORT}/"));
            }
            Event::WindowEvent { event: WindowEvent::CloseRequested, .. } => {
                if let Some(c) = core.as_mut() {
                    kill_tree(c);
                }
                if let Some(o) = ollama.as_mut() {
                    kill_tree(o);
                }
                *flow = ControlFlow::Exit;
            }
            _ => {}
        }
    });
}
