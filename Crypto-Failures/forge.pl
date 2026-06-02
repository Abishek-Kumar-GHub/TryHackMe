perl -e '
my $salt = "YE";
my $UA = "curl/8.19.0";
my $cookie = "YENCIDJawlk0sYEZPc8q5nsljoYEKv43Ipy3eU6YEGnxpHYznkWIYE/kurtMWJwcgYEcID71M7F6FQYEMAHXriSplBIYEFQ8RUcwIKvwYEWmvOkHVEjP.YEslOgYUPs.iMYE3td46X.SE.gYEQaa01vZUlS2YE9XNXpcgp/agYEh2SL16/K/FEYE5ctHi6AC896YEqFyCLc6gg42YEd9XPsFL7FOIYEpDYYAH71GowYEPnCSS1SvBZ2YEcGc2RgqcpqQYE5MEgJ13Cu2wYEBHVVrQBHLJU";

sub make_cookie {
    my ($text, $s) = @_;
    my $out = "";
    for (my $i = 0; $i < length($text); $i += 8) {
        $out .= crypt(substr($text, $i, 8), $s);
    }
    return $out;
}

my @keys = qw(secret password admin 1234 qwerty letmein abc123 
              crypto key flag thm tryhackme supersecret mysecret
              test hello world monkey dragon master 111111 pass
              secure encrypt cipher des crypt salt pepper);

for my $k (@keys) {
    my $test = make_cookie("guest:$UA:$k", $salt);
    if ($test eq $cookie) {
        print "FOUND KEY: $k\n";
        exit;
    }
}
print "Not in common list, need brute force\n";
'
