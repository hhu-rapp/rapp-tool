\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{hhuarticle}[2020/08/21 AI-Seminar LaTeX document class v1.4-no_beramono]

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}} % Options fallback.
\ProcessOptions\relax

\LoadClass[11pt,a4paper,twoside]{article}


%%% Configuration commands

\let\semester\date

\newcommand{\subject}[1]{%
  \renewcommand{\@subject}{#1}
  \renewcommand{\@subjectnl}{#1\\}}
\newcommand{\@subject}{}
\newcommand{\@subjectnl}{} % With linebreak at end.

%% Allows switching between colour and black/white printing
\newif\ifprintblackwhite
\printblackwhitefalse

\newcommand{\blackwhiteprint}{
  \printblackwhitetrue
  \pgfplotsset{cycle list name=hhubwcycle}
  \pgfplotsset{%
    /pgfplots/bar cycle list/.style={/pgfplots/cycle list name=hhubwbars}
  }
}


%%% Necessary packages

%% Allows direct insertion of umlauts (ä, ö, ü instead of \"a, \"o, \"u)
\RequirePackage[utf8]{inputenc}
\RequirePackage[T1]{fontenc}

\RequirePackage[nottoc]{tocbibind}
\RequirePackage{iflang} % Needed for language dependend distinctions

\RequirePackage{xcolor}
%% HHU Corporate Design colours
\definecolor{hhublue}{HTML}{006ab3} % Blau
\definecolor{hhudarkblue}{HTML}{003964} % Dunkelblau
\definecolor{hhuiceblue}{HTML}{b5cbd6} % Eisblau
\definecolor{hhucyan}{HTML}{57bab1} % Türkis
\definecolor{hhugreen}{HTML}{8cb110} % Grün
\definecolor{hhuorange}{HTML}{ee7f00} % Orange
\definecolor{hhured}{HTML}{be0a26} % Rot

\RequirePackage{ifthen}

\RequirePackage{tikz}
\RequirePackage{pgf,pgfplots}
%% Setup of colour cylce lists for pgfplots
\pgfplotscreateplotcyclelist{hhucolorcycle}{
  solid,hhublue,every mark/.append style={solid},mark=*\\
  dashed,hhured,every mark/.append style={solid},mark=square*\\
  dashdotted,hhugreen,every mark/.append style={solid},mark=diamond*\\
  dotted,hhuorange,every mark/.append style={solid},mark=triangle*\\
  densely dashed,hhucyan,every mark/.append style={solid},mark=star\\
  loosely dashed,hhublue,every mark/.append style={solid},mark=o\\
  loosely dotted,hhured,every mark/.append style={solid},mark=square\\
  densely dashed,hhugreen,every mark/.append style={solid},mark=diamond\\
  loosely dashdotted,hhuorange,every mark/.append style={solid},mark=triangle\\
  densely dotted,hhucyan,every mark/.append style={solid},mark=star\\
}
\pgfplotscreateplotcyclelist{hhubwcycle}{ % For black/white print
  solid,every mark/.append style={solid,fill=gray},mark=*\\
  dashed,every mark/.append style={solid,fill=gray},mark=square*\\
  dashdotted,every mark/.append style={solid,fill=gray},mark=diamond*\\
  dotted,every mark/.append style={solid,fill=gray},mark=triangle*\\
  densely dashed,every mark/.append style={solid},mark=star\\
  loosely dashed,every mark/.append style={solid},mark=o\\
  loosely dotted,every mark/.append style={solid},mark=square\\
  densely dashed,every mark/.append style={solid},mark=diamond\\
  loosely dashdotted,every mark/.append style={solid},mark=triangle\\
  densely dotted,every mark/.append style={solid},mark=star\\
}
%% The same for bar plots
\pgfplotscreateplotcyclelist{hhucolorbars}{
  {fill=hhublue!30!white, draw=hhublue, text=hhublue},
  {fill=hhured!30!white, draw=hhured, text=hhured},
  {fill=hhugreen!30!white, draw=hhugreen, text=hhugreen},
  {fill=hhuorange!30!white, draw=hhuorange, text=hhuorange},
  {fill=hhucyan!30!white, draw=hhucyan, text=hhucyan}
}
\pgfplotscreateplotcyclelist{hhubwbars}{
  {fill=black!75!white, draw=black},
  {fill=black!10!white, draw=black},
  {fill=black!65!white, draw=black},
  {fill=black!30!white, draw=black},
  {fill=black!50!white, draw=black}
}
%% Default colour cycle list
%% The colour cycle lists are further defined below.
%% Note that calling \blackwhiteprint switches this to hhubwcycle.
\pgfplotsset{cycle list name=hhucolorcycle}
\pgfplotsset{%
  /pgfplots/bar cycle list/.style={/pgfplots/cycle list name=hhucolorbars}
}



%%% Formatting and Typesetting

\pagestyle{headings}

\setlength{\textwidth}{14cm}
% % \setlength{\textheight}{23cm}

\setlength{\oddsidemargin}{0.9cm}
\setlength{\evensidemargin}{0cm}
\setlength{\marginparwidth}{2cm}

\RequirePackage{caption}
\captionsetup{width=0.9\textwidth,labelfont=bf,font=small}

%% Allow use of \frontmatter, \mainmatter, \appendix, and \backmatter
% \newcommand{\frontmatter}{
%   \cleardoublepage
%   \pagenumbering{roman}
% }

% \newcommand{\mainmatter}{
%   \cleardoublepage
%   \pagenumbering{arabic}
% }

\renewcommand{\appendix}{
  \clearpage
  {\LARGE\bf \appendixpagename}%
  \setcounter{section}{0}%
  \setcounter{subsection}{0}%
  \gdef\thesection{\@Alph\c@section}
  \let\section\appendix@section
}
\newcommand{\appendixpagename}{\iflanguage{ngerman}{Anhang}{Appendices}}
\newcommand\appendix@section[1]{%
  \refstepcounter{section}%
  \orig@section*{\appendixname{}~\thesection\hspace{1em}#1}%
  \addcontentsline{toc}{section}{\appendixname{}~\thesection\hspace{1em}#1}%
}
\let\orig@section\section

% \newcommand{\backmatter}{
%   \clearpage
%   \let\section\orig@section
%   \setcounter{secnumdepth}{0}
% }

%% Define link colors for hyperref package
\newcommand{\sethyperrefhhucolors}{%
  \hypersetup{
    linkcolor=hhublue,
    linkbordercolor=hhublue,
    menucolor=hhublue,
    menubordercolor=hhublue,
    citecolor=hhublue,
    citebordercolor=hhublue,
    filecolor=hhublue,
    filebordercolor=hhublue,
    urlcolor=hhublue,
    urlbordercolor=hhublue
  }
}

%% Define PDF meta data
\newcommand{\sethyperrefpdfinfos}{
  \hypersetup{
    pdfinfo={
      Title={\@title},
      Author={\@author},
      Subject={Seminararbeit}
    }
  }
}

%% Adapt lstlisting display
\newcommand{\lstkeyword}[1]{%
  \color{hhublue}\bfseries#1}
\newcommand{\lststring}[1]{%
  \color{hhudarkblue}#1}
\newcommand{\setlstlistingstyle}{
  \lstset{
    basicstyle=\small\ttfamily,
    numbers=left, numberstyle=\footnotesize,
    keywordstyle=\lstkeyword,
    commentstyle=\color{gray}\itshape,
    stringstyle=\lststring,
    showstringspaces=false,
    frame=tb,
  }
  \renewcommand*\thelstnumber{{\the\value{lstnumber}}:}
}

%% Adapt algorithmicx font
\newcommand{\algsmallfont}{\algrenewcommand\ALG@beginalgorithmic{\small}}

%%% Setup of title page

\RequirePackage{graphicx}

\newcommand{\@makeheader}{
  \vspace*{-4cm}
  \hspace{-1.54cm}
  \raisebox{-10mm}{
    \begin{minipage}[b]{4cm}
      \ifprintblackwhite%
        \includegraphics[width=6cm]{hhulogo-bw.pdf}%
      \else%
        \includegraphics[width=6cm]{hhulogo.pdf}%
      \fi
    \end{minipage}%
  }%
  \hfill
  % \begin{minipage}[c]{7.3cm}
  %   \vspace{8mm}
  %   \hfill
  %     {Professor Dr.~Jon Snow\linebreak}
  %   \hfill
  %     {Knows nothing\linebreak}
  % \end{minipage}
}

\renewcommand{\@maketitle}{%
  \null
  \vskip 2em%
  \begin{center}%
  \let \footnote \thanks
    {\LARGE \@title \par}%
    \vskip 0.5em%
    {\large
      \lineskip .5em%
      \begin{tabular}[t]{c}%
        \@author
      \end{tabular}\par}%
    \vskip 1em%
    {\large {%
      \@subjectnl % Line break is set by \subject command.
      \@date}}
    % \vskip 1em%
    % {\large \@date}%
  \end{center}%
  \par
  \vskip 1em
}

\renewcommand{\maketitle}{%
  \@makeheader
  \par
  \begingroup
    \renewcommand\thefootnote{\@fnsymbol\c@footnote}%
    \def\@makefnmark{\rlap{\@textsuperscript{\normalfont\@thefnmark}}}%
    \long\def\@makefntext##1{\parindent 1em\noindent
            \hb@xt@1.8em{%
                \hss\@textsuperscript{\normalfont\@thefnmark}}##1}%
    \if@twocolumn
      \ifnum \col@number=\@ne
        \@maketitle
      \else
        \twocolumn[\@maketitle]%
      \fi
    \else
      \global\@topnum\z@   % Prevents figures from going at top of page.
      \@maketitle
    \fi
    \thispagestyle{empty}\@thanks
  \endgroup
  \setcounter{footnote}{0}%
  \global\let\thanks\relax
  \global\let\maketitle\relax
  \global\let\@maketitle\relax
  \global\let\@thanks\@empty
  \global\let\@author\@empty
  \global\let\@date\@empty
  \global\let\@title\@empty
  \global\let\title\relax
  \global\let\author\relax
  \global\let\date\relax
  \global\let\and\relax
}

%%% Nicer handling commands

\let\orig@section\section
\renewcommand{\appendix}{
  \section*{\LARGE\appendixpagename}%
  \setcounter{section}{0}%
  \setcounter{subsection}{0}%
  \gdef\thesection{\@Alph\c@section}%
  \let\section\appendix@section%
}
% \newcommand{\appendixpagename}{\iflanguage{ngerman}{Anhang}{Appendices}}
\renewcommand{\appendix@section}[2][\@nil]{%
  \refstepcounter{section}%
  \orig@section*{\thesection\hspace{1em}#2}%
  \def\tmp{#1}%
  \ifx\tmp\@nnil% % Puts the optional short title into the ToC if not empty
    \addcontentsline{toc}{section}{\appendixname{}~\thesection\hspace{1em}#2}%
  \else%
    \addcontentsline{toc}{section}{\appendixname{}~\thesection\hspace{1em}#1}%
  \fi%
  \markboth{\thesection\hspace{1em}\MakeUppercase{#2}}{}%
}


\newcommand{\backmatter}{
  \let\section\orig@section
  \setcounter{secnumdepth}{0}
}
